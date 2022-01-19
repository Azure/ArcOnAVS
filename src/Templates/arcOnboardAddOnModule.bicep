param vCenterId string
param avsPrivateCloudName string

resource arcAddOnAVS 'Microsoft.AVS/privateClouds/addons@2022-05-01' = {
	name: '${avsPrivateCloudName}/arc'
	properties: {
		addonType: 'Arc'
		vCenter: vCenterId
	}
}