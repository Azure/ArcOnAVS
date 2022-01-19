param arcManagedIdentityId string
param avsPrivateCloudName string
param avsResourceGroupName string
param arcResourceGroupName string

var avsArcAddOnName = 'arc'
var resourceBridgeName = '${avsPrivateCloudName}-resource-bridge'
var k8sExtensionName = 'azure-vmwareoperator'
var customLocationName = '${avsPrivateCloudName}-custom-location'
var vCenterName = '${avsPrivateCloudName}-vcenter'

var deploymentScriptToDeboardArcName = 'deploymentScriptToDeboardArc'
var location = resourceGroup().location
var arcAddonResourceId = '/subscriptions/${subscription().subscriptionId}/resourceGroups/${avsResourceGroupName}/providers/Microsoft.AVS/privateClouds/${avsPrivateCloudName}/addons/${avsArcAddOnName}'

resource deploymentScriptToDeboardArc 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
	name: deploymentScriptToDeboardArcName
	location: location
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
			containerGroupName: '${avsPrivateCloudName}-arc-deboard-aci-container-group'
		}
		azPowerShellVersion: '6.4'
		arguments: '-arcAddonResourceId ${arcAddonResourceId} -vCenterName ${vCenterName} -customLocationName ${customLocationName} -k8sExtensionName ${k8sExtensionName} -resourceBridgeName ${resourceBridgeName} -arcResourceGroupName ${arcResourceGroupName} -avsResourceGroupName ${avsResourceGroupName}'
		scriptContent: '''
			Param(
				[parameter(Mandatory=$true)][string] $arcAddonResourceId,
				[parameter(Mandatory=$true)][string] $vCenterName,
				[parameter(Mandatory=$true)][string] $customLocationName,
				[parameter(Mandatory=$true)][string] $k8sExtensionName,
				[parameter(Mandatory=$true)][string] $resourceBridgeName,
				[parameter(Mandatory=$true)][string] $arcResourceGroupName,
				[parameter(Mandatory=$true)][string] $avsResourceGroupName
			)
			
			Write-Host "Deleting $arcAddonResourceId"
			Remove-AzResource -ResourceId $arcAddonResourceId -Force -ErrorAction Stop
			Write-Host "Deleted $arcAddonResourceId successfully!"
			
			Write-Host "Deleting $vCenterName"
			Remove-AzResource -ResourceName $vCenterName -ResourceType 'Microsoft.ConnectedVMwarevSphere/vcenters' -ResourceGroupName $arcResourceGroupName -Force
			Write-Host "Deleted $vCenterName successfully!"
			
			Write-Host "Deleting $customLocationName"
			Remove-AzResource -ResourceName $customLocationName -ResourceType 'Microsoft.ExtendedLocation/customLocations' -ResourceGroupName $arcResourceGroupName -Force
			Write-Host "Deleted $customLocationName successfully!"
			
			Write-Host "Deleting $k8sExtensionName"
			Remove-AzResource -ResourceName $resourceBridgeName -ResourceType 'Microsoft.ResourceConnector/appliances' -ExtensionResourceName $k8sExtensionName -ExtensionResourceType 'Microsoft.KubernetesConfiguration/extensions' -ResourceGroupName $arcResourceGroupName -Force
			Write-Host "Deleted $k8sExtensionName successfully!"
			
			Write-Host "Deleting $resourceBridgeName"
			Remove-AzResource -ResourceName $resourceBridgeName -ResourceType 'Microsoft.ResourceConnector/appliances' -ResourceGroupName $arcResourceGroupName -Force
			Write-Host "Deleted $resourceBridgeName successfully!"
			
			Write-Host "Arc Deboard Completed!"
		'''
		timeout: 'PT30M'
		cleanupPreference: 'OnSuccess'
		retentionInterval: 'P1D'
	}
}