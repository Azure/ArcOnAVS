targetScope = 'subscription'

param avsResourceGroupName string
param avsPrivateCloudName string
param avsPrivateCloudLocation string = 'westeurope'
param appliancePublicKey string
param type string

var arcResourceGroupName = '${avsPrivateCloudName}-arc-rg'
var arcManagedIdentityName = '${avsPrivateCloudName}-arc-managed-identity'
var contributorRoleDefinitionId = '/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c'

resource arcResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
	name: arcResourceGroupName
	location: avsPrivateCloudLocation
}

module arcManagedIdentityModule './arcManageIdentityModule.bicep' = {
	name: 'arcManagedIdentityModule'
	scope: arcResourceGroup
	params: {
		arcManagedIdentityName: arcManagedIdentityName
		contributorRoleDefinitionId: contributorRoleDefinitionId
	}
}

module avsSDDCPermissionToArcManagedIdentityModule './avsSDDCPermissionToArcManagedIdentityModule.bicep' = {
	name: 'avsSDDCPermissionToArcManagedIdentityModule'
	scope: resourceGroup(avsResourceGroupName)
	dependsOn: [
		arcManagedIdentityModule
	]
	params: {
		arcManagedIdentityPricipalId: arcManagedIdentityModule.outputs.arcManagedIdentityPricipalId
		contributorRoleDefinitionId: contributorRoleDefinitionId
	}
}

module arcOnboardModule './arcOnboardModule.bicep' = if (type == 'onboard') {
	name: 'arcOnboardModule'
	scope: arcResourceGroup
	dependsOn: [
		arcManagedIdentityModule
	]
	params: {
		avsPrivateCloudName: avsPrivateCloudName
		appliancePublicKey: appliancePublicKey
		arcManagedIdentityId: arcManagedIdentityModule.outputs.arcManagedIdentityId
	}
}

module arcOnboardAddOnModule './arcOnboardAddOnModule.bicep' = if (type == 'onboard') {
	name: 'arcOnboardAddOnModule'
	scope: resourceGroup(avsResourceGroupName)
	dependsOn: [
		arcOnboardModule
	]
	params: {
		avsPrivateCloudName: avsPrivateCloudName
		vCenterId: arcOnboardModule.outputs.vCenterId
	}
}

module arcDeboardModule './arcDeboardModule.bicep' = if (type == 'deboard') {
	name: 'arcDeboardModule'
	scope: arcResourceGroup
	dependsOn: [
		arcManagedIdentityModule
	]
	params: {
		arcManagedIdentityId: arcManagedIdentityModule.outputs.arcManagedIdentityId
		avsPrivateCloudName: avsPrivateCloudName
		avsResourceGroupName: avsResourceGroupName
		arcResourceGroupName: arcResourceGroupName
	}
}