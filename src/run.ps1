[CmdletBinding()]
Param(
    [parameter(Mandatory=$true)][string]$Operation,
    [Parameter(Mandatory=$true)] [string] $FilePath,
    [Parameter(Mandatory=$false)] [string] $LogLevel = 'INFO',
    [Parameter(Mandatory=$false)] [bool] $isAutomated = $false # isAutomated Parameter is set to true if it is an automation testing Run.
                                                                # In case this param is true, we use az login --identity, which logs in Azure VM's identity
                                                                # and skips the confirm prompts.
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
    "arcappliance"="";
    "connectedvmware"="";
    "k8s-extension"="";
    "customlocation"=""};

$logFile = Join-Path $PSScriptRoot "arcavs-output.log"

function logH2($msg) {
    $msgFull = "==> $msg"
    Write-Host -ForegroundColor Magenta $msgFull
    Add-Content -Value "$msgFull" -Path $logFile
}

function logText($msg) {
    Write-Host "$msg"
    Add-Content -Value "$msg" -Path $logFile
}

function logWarn($msg) {
    Write-Host -ForegroundColor Yellow $msg
    Add-Content -Value "$msg" -Path $logFile
}

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

function getLatestAzVersion() {
    $gitUrl = "https://raw.githubusercontent.com/Azure/azure-cli/main/src/azure-cli/setup.py"
    try {
        $response = Invoke-WebRequest -Uri $gitUrl -TimeoutSec 30
    }
    catch {
        logWarn "Failed to get the latest version from '$gitUrl': $($_.Exception.Message)"
        return $null
    }
    if ($response.StatusCode -ne 200) {
        logWarn "Failed to fetch the latest version from '$gitUrl' with status code '$($response.StatusCode)' and reason '$($response.StatusDescription)'"
        return $null
    }
    $content = $response.Content
    foreach ($line in $content -split "`n") {
        if ($line.StartsWith('VERSION')) {
            $match = [System.Text.RegularExpressions.Regex]::Match($line, 'VERSION = "(.*)"')
            if ($match.Success) {
                return $match.Groups[1].Value
            }
        }
    }
    logWarn "Failed to extract the latest version from the content of '$gitUrl'"
    return $null
}

function shouldInstallAzCli() {
    # This function returns a boolean value, but any undirected / uncaptured stdout
    # inside the function might be interpreted as true value by the caller.
    # We can redirect using *>> to avoid this.
    logH2 "Validating and installing 64-bit azure-cli"
    $azCmd = (Get-Command az -ErrorAction SilentlyContinue)
    if ($null -eq $azCmd) {
        logText "Azure CLI is not installed. Installing..."
        return $true
    }

    $currentAzVersion = az version --query '\"azure-cli\"' -o tsv 2>> $logFile
    logText "Azure CLI version $currentAzVersion found in PATH at location: '$($azCmd.Source)'"
    $azVersion = az --version *>&1;
    $azVersionLines = $azVersion -split "`n"
    
    $pyLoc = $azVersionLines | Where-Object { $_ -match "^Python location" }
    if ($null -eq $pyLoc) {
        logWarn "Warning: Python location could not be found from the output of az --version:`n$($azVersionLines -join "`n"))"
        return $true
    }
    logText $pyLoc
    $pythonExe = $pyLoc -replace "^Python location '(.+?)'$", '$1'
    try {
        logText "Determining the bitness of Python at '$pythonExe'"
        $arch = & $pythonExe -c "import struct; print(struct.calcsize('P') * 8)";
        if ($arch -lt 64) {
            logText "Azure CLI is $arch-bit. Installing 64-bit version..."
            return $true
        }
    }
    catch {
        logText "Warning: Python version could not be determined from the output of az --version:`n$($azVersionLines -join "`n"))"
        return $true
    }

    logH2 "$arch-bit Azure CLI is already installed. Checking for updates..."
    $latestAzVersion = getLatestAzVersion
    if ($latestAzVersion -and ($latestAzVersion -ne $currentAzVersion)) {
        logText "A newer version of Azure CLI ($latestAzVersion) is available, installing it..."
        return $true
    }
    logText "Azure CLI is up to date."
    return $false
}

function installAzCli64Bit() {
    $azCliMsi = "https://aka.ms/installazurecliwindowsx64"
    $azCliMsiPath = Join-Path $PSScriptRoot "AzureCLI.msi"
    $msiInstallLogPath = Join-Path $env:Temp "azInstall.log"
    logText "Downloading Azure CLI 64-bit MSI from $azCliMsi to $azCliMsiPath"
    Invoke-WebRequest -Uri $azCliMsi -OutFile $azCliMsiPath
    logText "Azure CLI MSI installation log will be written to $msiInstallLogPath"
    logH2 "Installing Azure CLI. This might take a while..."
    $p = Start-Process msiexec.exe -Wait -Passthru -ArgumentList "/i `"$azCliMsiPath`" /quiet /qn /norestart /log `"$msiInstallLogPath`""
    $exitCode = $p.ExitCode
    if ($exitCode -ne 0) {
        throw "Azure CLI installation failed with exit code $exitCode. See $msiInstallLogPath for additional details."
    }
    $azCmdDir = Join-Path $env:ProgramFiles "Microsoft SDKs\Azure\CLI2\wbin"
    [System.Environment]::SetEnvironmentVariable('PATH', $azCmdDir + ';' + $Env:PATH)
    logText "Azure CLI has been installed."
}

function installAzExtension($name, $version)
{
    if($version -eq "")
    {
        az extension add --name $name --upgrade
    }
    elseif(!(checkIfAzExtensionIsInstalled -name $name -version $version))
    {
        Write-Host "Installing extension $name of version $version..."
        az extension add --name $name --version $version --upgrade
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

if (shouldInstallAzCli) {
    installAzCli64Bit
}

function fetchPythonLocation()
{
    $azVersion = az --version *>&1;
    $azVersionLines = $azVersion -split "`n"
    
    $pyLoc = $azVersionLines | Where-Object { $_ -match "^Python location" }
    $pythonExe = $pyLoc -replace "^Python location '(.+?)'$", '$1'
    return $pythonExe
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

$pythonExe = fetchPythonLocation

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

. $pythonExe .\appliance_setup\run.py $Operation $FilePath $LogLevel $isAutomated
$OperationExitCode = $LASTEXITCODE

printOperationStatusMessage -Operation $Operation -OperationExitCode $OperationExitCode

$ProgressPreference = 'Continue'

Exit $OperationExitCode