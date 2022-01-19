param arcManagedIdentityPricipalId string
param contributorRoleDefinitionId string

var arcManagedIdentityAvsRgRoleAssignmentName = guid(resourceGroup().id, arcManagedIdentityPricipalId, 'ContributorRole')

resource arcManagedIdentityAvsRgRoleAssignment 'Microsoft.Authorization/roleAssignments@2021-04-01-preview' = {
	name: arcManagedIdentityAvsRgRoleAssignmentName
	scope: resourceGroup()
	properties: {
		principalId: arcManagedIdentityPricipalId
		principalType: 'ServicePrincipal'
		roleDefinitionId: contributorRoleDefinitionId
	}
}
