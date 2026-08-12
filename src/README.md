# Prerequisites
To deploy Arc for Azure VMware Solution, you need to ensure the following prerequisites are met.

For more information, please visit: https://learn.microsoft.com/en-us/azure/azure-vmware/deploy-arc-for-azure-vmware-solution

## Providers
The following Register features are for provider registration using Azure CLI.

```bash
az provider register --namespace Microsoft.ConnectedVMwarevSphere   
az provider register --namespace Microsoft.ExtendedLocation  
az provider register --namespace Microsoft.KubernetesConfiguration   
az provider register --namespace Microsoft.ResourceConnector    
az provider register --namespace Microsoft.AVS
```

## Networking
From the management server you need to following ports open into the AVS Private Cloud:

|Service|Port|Destination|Notes|
|--------|----|----------|-----|
|vCenter|443|vc.<id>.<region>.avs.azure.com|Used for the ArcOnAvs script|
|ESXi Hosts|443|ESXi Segment|For example if our AVS network is 10.0.16.0/22 then 10.0.17.0/25|
|AzureArc Resource Bridge|22,443,6443|AzureArc-Segment|The AzureArc segment created /28|

# Configuration

```json
{
  "subscriptionId": "",
  "resourceGroup": "",
  "privateCloud": "",
  "isStatic": true,
  "staticIpNetworkDetails": { 
    "networkForApplianceVM": "", 
    "networkCIDRForApplianceVM": ""
  },
  "applianceCredentials": { 
    "username": "", 
    "password": "" 
  }, 
  "applianceProxyDetails": { 
    "http": "", 
    "https": "", 
    "noProxy": "", 
    "certificateFilePath": "" 
  }, 
  "managementProxyDetails": { 
    "http": "", 
    "https": "", 
    "noProxy": "", 
    "certificateFilePath": "" 
  }
}
```

To use the cloudadmin credentials the values must be empty on the ```applianceCredentials```.

## Regions
If your AVS region is not supported you can adjust the location as follow:

|AVS Region|Recommended Region|Configuration|
|----------|--------------------|-------------|
|Switzerland North|West Europe|```"location": "westeurope"```|

```json
{
  "subscriptionId": "",
  "resourceGroup": "",
  "privateCloud": "",
  "location": "westeurope",
  ...
}
```