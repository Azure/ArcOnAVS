param arcManagedIdentityName string
param contributorRoleDefinitionId string

var location = resourceGroup().location
var arcManagedIdentityArcRgRoleAssignmentName = guid(resourceGroup().id, arcManagedIdentityName, 'ContributorRole')

resource arcManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
	name: arcManagedIdentityName
	location: location
}

resource arcManagedIdentityArcRgRoleAssignment 'Microsoft.Authorization/roleAssignments@2021-04-01-preview' = {
	name: arcManagedIdentityArcRgRoleAssignmentName
	scope: resourceGroup()
	properties: {
		principalId: arcManagedIdentity.properties.principalId
		principalType: 'ServicePrincipal'
		roleDefinitionId: contributorRoleDefinitionId
	}
}

output arcManagedIdentityPricipalId string = arcManagedIdentity.properties.principalId
output arcManagedIdentityId string = arcManagedIdentity.id