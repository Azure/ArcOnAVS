[CmdletBinding()]
Param(
    [parameter(Mandatory=$true)][string]$Operation,
    [Parameter(Mandatory=$true)] [string] $FilePath,
    [Parameter(Mandatory=$false)] [string] $LogLevel = 'INFO',
    [Parameter(Mandatory=$false)] [bool] $isAutomated = $false, # isAutomated Parameter is set to true if it is an automation testing Run. 
                                                                # In case this param is true, we use az login --identity, which logs in Azure VM's identity
                                                                # and skips the confirm prompts.
    [Parameter(Mandatory=$false)] [string] $VmWareSPObjectID # VmWareSPObjectID is the SP Object ID. This is passed down to the for setting up logs for connected vmware team.
)

$majorVersion = $PSVersionTable.PSVersion.Major
$minorVersion = $PSVersionTable.PSVersion.Minor
$version = [decimal]"$majorVersion.$minorVersion"

if($version -lt 5.1)
{
    throw "Minimum supported powershell version is 5.1. Please upgrade your powershell version."
}

New-Item -Force -Path "." -Name ".temp" -ItemType "directory"

$ProgressPreference = 'SilentlyContinue'


# Use empty string for the version to fetch latest CLI version
$AzExtensions=@{
    "arcappliance"="0.2.21";
    "connectedvmware"="0.1.6";
    "k8s-extension"="1.2.2";
    "customlocation"="0.1.3"};

function checkIfAzExtensionIsInstalled($name, $version)
{
    $list = (az extension list | ConvertFrom-Json)
    foreach($ex in $list)
    {
        if($ex.name -eq $name -and $ex.version -eq $version)
        {
            return $true
        }
    }
    return $false
}

function setPathForAzCliCert($config)
{
    if(![string]::IsNullOrEmpty($config.proxyDetails) -and ![string]::IsNullOrEmpty($config.proxyDetails.certificateFilePath))
    {
        $certAbsolutePath=Resolve-Path -Path $config.proxyDetails.certificateFilePath
        $env:REQUESTS_CA_BUNDLE=$certAbsolutePath
    }
}

function activate_venv()
{
    Write-Host "Activating python venv..."
    .\.temp\.env\Scripts\activate.ps1
}

function deactivate_venv()
{
    Write-Host "De-ctivating python venv..."
    deactivate
}

function installAzExtension($name, $version)
{
    if(!(checkIfAzExtensionIsInstalled -name $name -version $version))
    {
        Write-Host "Installing extension $name of version $version..."
        if("$version" -eq "")
        {
            az extension add --name $name --upgrade
        }
        else
        {
            az extension add --name $name --version $version --upgrade
        }
    }
}

function printOperationStatusMessage($Operation, $OperationExitCode)
{
    if($OperationExitCode -eq 0)
    {
        Write-Host "$Operation operation was successfull." -ForegroundColor green
    }
    else
    {
        Write-Host "$Operation operation failed! Please check stderr or equivalent for more details." -ForegroundColor red
    }
}

$config = Get-Content -Path $FilePath | ConvertFrom-Json
if(![string]::IsNullOrEmpty($config.proxyDetails))
{
    $config = $config.proxyDetails
    if(![string]::IsNullOrEmpty($config.http))
    {
        $env:http_proxy=$config.http
        $env:HTTP_PROXY=$env:http_proxy
    }

    if(![string]::IsNullOrEmpty($config.https))
    {
        $env:https_proxy=$config.https
        $env:HTTPS_PROXY=$env:https_proxy
    }

    if(![string]::IsNullOrEmpty($config.noProxy))
    {
        $env:no_proxy=$config.noProxy
        $env:NO_PROXY=$env:no_proxy
    }
    $proxyURL = $env:https_proxy
    $proxyAddr=$null
    $proxyUsername=$null
    $proxyPassword=$null
    if(![string]::IsNullOrEmpty($proxyURL) -and $proxyURL.Contains("@"))
    {
        $x=$proxyURL.Split("//")
        $proto=$x[0]
        $x=$x[2].Split("@")
        $userPass=$x[0]
        $proxyAddr=$proto + "//" + $x[1]
        $x=$userPass.Split(":")
        $proxyUsername=$x[0]
        $proxyPassword=$x[1]
    }
    else
    {
        $proxyAddr=$proxyURL
    }

    $credential = $null
    if($proxyPassword)
    {
        $password = ConvertTo-SecureString -String $proxyPassword -AsPlainText -Force
        $credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $proxyUsername,$password
    }

    [system.net.webrequest]::defaultwebproxy = new-object system.net.webproxy($proxyAddr)
    [system.net.webrequest]::defaultwebproxy.credentials = $credential
    [system.net.webrequest]::defaultwebproxy.BypassProxyOnLocal = $true
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

try {
    $bitSize = py -c "import struct; print(struct.calcsize('P') * 8)"
    if ($bitSize -ne "64") {
        throw "Python is not 64-bit"
    }
    Write-Host "64-bit python is already installed"
}
catch
{
    Write-Host "Installing python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.8.8/python-3.8.8-amd64.exe" -OutFile ".temp/python-3.8.8-amd64.exe"
    $p = Start-Process .\.temp\python-3.8.8-amd64.exe -Wait -PassThru -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
    $exitCode = $p.ExitCode
    if($exitCode -ne 0)
    {
        throw "Python installation failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Enabling long path support for python..."
Start-Process powershell.exe -verb runas -ArgumentList "Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem -Name LongPathsEnabled -Value 1" -Wait

$config = Get-Content -Path $FilePath | ConvertFrom-Json


if((Test-Path -Path '.temp\govc.exe') -eq $false)
{
    Write-Host "Downloading govc..."
    Invoke-WebRequest https://github.com/vmware/govmomi/releases/download/v0.24.0/govc_windows_amd64.exe.zip -OutFile .temp/govc_windows_amd64.exe.zip
    Expand-Archive -Force .temp\govc_windows_amd64.exe.zip -DestinationPath .temp\
    Rename-Item -Force -Path ".temp/govc_windows_amd64.exe" -NewName "govc.exe"
}

Write-Host "Creating python venv..."
py -m venv .temp\.env

activate_venv

if(![string]::IsNullOrEmpty($config.proxyDetails) -and ![string]::IsNullOrEmpty($config.proxyDetails.certificateFilePath))
{
    py -m pip install --cert $config.proxyDetails.certificateFilePath --upgrade pip
    py -m pip install --cert $config.proxyDetails.certificateFilePath azure-cli
    py -m pip install --cert $config.proxyDetails.certificateFilePath -r .\appliance_setup\dependencies
}
else
{
    py -m pip install --upgrade pip
    py -m pip install azure-cli
    py -m pip install -r .\appliance_setup\dependencies
}

$az_account_check_token = az account get-access-token
if ($az_account_check_token -eq $null){
    setPathForAzCliCert -config $config
    if ($isAutomated)
	{
        az login --identity
	}
    else
	{
        az login --use-device-code
	}
}


foreach($x in $AzExtensions.GetEnumerator())
{   
    installAzExtension -name $x.Name -version $x.Value
}

py .\appliance_setup\run.py $Operation $FilePath $LogLevel $isAutomated $VmWareSPObjectID
$OperationExitCode = $LASTEXITCODE

printOperationStatusMessage -Operation $Operation -OperationExitCode $OperationExitCode

deactivate_venv

$ProgressPreference = 'Continue'

Exit $OperationExitCode