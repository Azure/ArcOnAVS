# Helper script for enabling ARC on Azure VMWare Solution

This helper script is provided to help you simplify the onboarding to the preview of ARC on Azure VMWare Solution.

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

9. Internet should be enabled in Azure VMWare Solution SDDC.

10. Provide required inputs in `config_avs.json`

## Using the script

The script provides `onboard` and `offboard` commands.

### On a Windows machine

Open a PowerShell window and run the following command. You will need to bypass execution policy as the script is not signed.
As with any script downloaded from the internet, do read its contents before running it.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\run.ps1 -Operation <onboard/offboard> -FilePath <path_to_config_avs.json>
```

### On a Linux machine

Use commands as follows:

```bash
sudo chmod +x run.sh 
sudo bash run.sh <onboard/offboard> <path_to_config_avs.json>
```

## Commands Description

### `onboard` command

Onboard command does following:

1. Downloads and installs required tools to be able to execute preview software from jump box (az cli tools, python etc.), if not present already. 

2. Creates an Azure VMware Solution segment as per details if not present already. Creates DNS server and zones if not present already. Fetch vCenter credentials. 

3. Creates template for Arc Appliance and takes snapshot from template created. 

4. Deploys the Arc for Azure VMware Solution appliance VM. 

5. Creates an ARM resource for the appliance. 

6. Creates a Kubernetes extension resource for azure VMware. 

7. Creates a custom location.  

8. Creates an Azure representation of the vCenter. 

9. Links the vCenter resource to the Azure VMware Solution Private Cloud resource. 

### `offboard` command

Offboard command does the following operations:

1. Download and install required tools to be able to execute preview software from jump box (az cli tools, python etc.), if not present already. 

2. De-links the vCenter resource from the Azure VMware Solution Private cloud resource. 

3. Deletes the azure representation of the vCenter. 

4. Deletes the Custom Location resource, the Kubernetes extension for Azure VMware operator, the ARM resource for the appliance 

5. Deletes the appliance VM. 

This command is provided to create a clean slate before retrying in case of failures.

## Feedback

In case of any questions/feedback fill this(https://aka.ms/ArcOnAVSFeedbackForm) form and we will reach out to you.

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
