param avsPrivateCloudName string
param appliancePublicKey string
param arcManagedIdentityId string

var applianceArmResourceName = '${avsPrivateCloudName}-resource-bridge'
var deploymentScriptToCheckApplianceStatusName = '${applianceArmResourceName}-status-check-deployment-script'
var k8sExtensionName = 'azure-vmwareoperator'
var customLocationName = '${avsPrivateCloudName}-custom-location'
var vCenterName = '${avsPrivateCloudName}-vcenter'
var location = resourceGroup().location
var vmwareRpSpId = '46b1b4eb-ab16-4ce8-aa55-096807312417'


var vCenterIP = '10.0.0.2'
var vCenterPort = 443
var vCenterUserName = 'cloudadmin@vsphere.local'
var vCenterPassword = '!1mt@tZ52M5l'

resource applianceArmResource 'Microsoft.ResourceConnector/appliances@2021-10-31-preview' = {
	name: applianceArmResourceName
	location: location
	identity: {
		type: 'SystemAssigned'
	}
	properties: {
		distro: 'AKSEdge'
		infrastructureConfig: {
			provider: 'VMWare'
		}
		publicKey: base64ToString(appliancePublicKey)
	}
}

resource deploymentScriptToCheckApplianceStatus 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
	name: deploymentScriptToCheckApplianceStatusName
	location: location
	dependsOn: [
		applianceArmResource
	]
	kind: 'AzurePowerShell'
	identity: {
		type: 'UserAssigned'
		userAssignedIdentities: {
			'${arcManagedIdentityId}': {}
		}
	}
	properties: {
		forceUpdateTag: '1'
		containerSettings: {
			containerGroupName: '${applianceArmResourceName}-status-check-aci-container-group'
		}
		azPowerShellVersion: '6.4'
		arguments: '-resourceGroupName ${resourceGroup().name} -applianceArmResourceName ${applianceArmResourceName}'
		scriptContent: '''
			Param(
				[parameter(Mandatory=$true)][string]$resourceGroupName,
				[Parameter(Mandatory=$true)] [string]$applianceArmResourceName
			)
			
			Write-Host "Checking status of Resource Bridge"
			
			$status = "NotChecked"
			do {
				$applianceArmResource = Get-AzResource -ResourceType "Microsoft.ResourceConnector/appliances" -ResourceGroupName $resourceGroupName -ResourceName $applianceArmResourceName
				$status = $applianceArmResource.Properties.status
				Write-Host "Resource Bridge is in $status state."
				Start-Sleep -Seconds 60
			}while($status -ne "Running")
		'''
		timeout: 'PT30M'
		cleanupPreference: 'OnSuccess'
		retentionInterval: 'P1D'
	}
}

resource k8sExtension 'Microsoft.KubernetesConfiguration/extensions@2021-09-01' = {
	name: k8sExtensionName
	location: location
	dependsOn: [
		deploymentScriptToCheckApplianceStatus
	]
	scope: applianceArmResource
	identity: {
		type: 'SystemAssigned'
	}
	properties: {
		extensionType: 'Microsoft.AVS'
		autoUpgradeMinorVersion: true
		releaseTrain: 'stable'
		scope: {
			cluster: {
				releaseNamespace: k8sExtensionName
			}
		}
		configurationSettings: {
			'Microsoft.CustomLocation.ServiceAccount': '${k8sExtensionName}--config'
			'global.rpObjectId': vmwareRpSpId
		}
		configurationProtectedSettings: {
		}
	}
}

resource customLocation 'Microsoft.ExtendedLocation/customLocations@2021-08-15' = {
	name: customLocationName
	location: location
	dependsOn: [
		k8sExtension
	]
	properties: {
		clusterExtensionIds: [
			k8sExtension.id
		]
		displayName: customLocationName
		hostResourceId: applianceArmResource.id
		hostType: 'Kubernetes'
		namespace: customLocationName
	}
}

resource connectVCenter 'Microsoft.ConnectedVMwarevSphere/vcenters@2020-10-01-preview' = {
	name: vCenterName
	location: location
	dependsOn: [
		customLocation
	]
	extendedLocation: {
		type: 'CustomLocation'
		name: customLocation.id
	}
	properties: {
		fqdn: vCenterIP
		port: vCenterPort
		credentials: {
			username: vCenterUserName
			password: vCenterPassword
		}
	}
}

output vCenterId string = connectVCenter.id