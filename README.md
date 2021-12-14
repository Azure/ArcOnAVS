# Helper script for Arc enabled AVS

This helper script is provided to help you simplify the onboarding to the preview of Arc enabled AVS. For more details, see [the private preview GitHub repo](https://github.com/Azure/ArcOnAVS)

**Note**: The link takes you to a private GitHub repo to access which you will need to be signed into GitHub and be provided access to the repo.

## Prerequisites

Ensure you meet all the prerequisites mentioned below:

1. A jump box Virtual Machine (VM) with network access to the Azure VMware Solution vCenter. From the jump-box VM, ensure you have access to vCenter and NSX-T portals. 

2. Internet access from jump box VM.

3. Your Azure Subscription needs to get whitelisting for private preview. Resource group in the subscription where you have owner/contributor role.

4. Have a minimum of 3 free non-overlapping IPs addresses.

5. Verify that your vCenter Server is 6.7 or above.

6. A resource pool with minimum free capacity of 16 GB of RAM, 4 vCPUs.

7. A datastore with minimum 100 GB of free disk space that is available through the resource pool.

8. On the vCenter Server, allow inbound connections on TCP port 443, so that the Arc resource bridge and VMware cluster extension can communicate with the vCenter server.
(As of today, only the default port of 443 is supported if you use a different port, Appliance VM creation will fail) 

9. Internet access from AVS SDDC.

10. Provide required inputs in `config_avs.json`

## Using the script

The script provides `onboard` and `deboard` commands.

### On a Windows machine

Open a PowerShell window and run the following command. You will need to bypass execution policy as the script is not signed.
As with any script downloaded from the internet, do read its contents before running it.

```powershell
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\run.ps1 -Operation <onboard/deboard> -FilePath <path_to_config_avs.json>
```

### On a Linux machine

Use commands as follows:

```bash
	sudo chmod +x run.sh 
	sudo bash run.sh <onboard/deboard> <path_to_config_avs.json>
```

## Commands Description

### `onboard` command

Onboard command does following:

1. Downloads and installs [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli), [Python](https://www.python.org/downloads/) and [govc](https://github.com/vmware/govmomi/releases).

2. Creates a python virtual environment in .temp directory

3. Installs ARC related azure-cli extensions

4. Creates required NSX components such as segment if they don't exist already etc.

3. Ensures all the required Azure resource providers are registered. Checks if all the required feature flags are enabled for the Azure subscription.

3. Creates a VM template from OVA.

4. Creates a snapshot of the VM template created.

5. Deploys the appliance VM in the vCenter based on the snapshot.

6. Creates an ARM representation of appliance VM as Resource Bridge in Azure.

7. Installs `azure-vmwareoperator` k8s cluster extension on the Appliance.

8. Creates a Custom Location representing your VMWare vSphere environment.

9. Creates an Azure representation of your vCenter.

10. Registers Azure representation of your vCenter with Azure Arc.

### `deboard` command

Deboard command does the following operations:

1. Un-registers Azure representation of your vCenter with Azure Arc.

2. Deletes Azure representation of your vCenter.

3. Deletes Custom Location representing your VMWare vSphere environment.

4. Deletes the `azure-vmwareoperator` cluster extension.

5. Deletes ARM representation of appliance VM.

6. Deletes the appliance VM (on your vCenter).

This command is provided to create a clean slate before retrying in case of failures.

## Feedback

In case of any questions/feedback reach out to arc-vmware-feedback@microsoft.com

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
