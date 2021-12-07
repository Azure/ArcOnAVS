# Helper script for Arc enabled VMware vSphere onboarding

This helper script is provided to help you simplify the onboarding to the private preview of Arc enabled VMware vSphere. For more details, see [the private preview GitHub repo](https://github.com/Azure/azure-arc-enabled-vmware-vsphere-preview/)

**Note**: The link takes you to a private GitHub repo to access which you will need to be signed into GitHub and be provided access to the repo.

## Prerequisites

Ensure you meet all the prerequisites mentioned in [this article](https://aka.ms/arc-connect-vcenter-pp).

At the minimum:

1. You should've already signed up for the Arc enabled VMware vSphere private preview using the [sign-up form](https://aka.ms/arc-vmware-sign-up) and gotten a confirmation from the Arc product team that your subscription has been enabled for the private preview.
2. Downloaded the OVA file needed.
3. Provide required inputs in `config.json`

## Using the script

The script provides `prepare`, `create` and `delete` commands.

### On a Windows machine

1. Open a PowerShell window and run the following command before running the script. The script is an not signed. So you will need to bypass execution policy. As with any script downloaded from the internet, do read its contents before running it.

    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

2. Use command as follows:

    ```powershell
    .\run.ps1 <prepare/create/delete> config.json
    ```

### On a Linux machine

1. Use command as follows:

    ```bash
    bash run.sh <prepare/create/delete> config.json
    ```

## Commands Description

### `Prepare` command

Prepare command does the following operations:

1. Downloads and installs [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli), [Python](https://www.python.org/downloads/) and [govc](https://github.com/vmware/govmomi/releases).

2. Checks if all the required feature flags are enabled for the Azure subscription. Ensures all the required Azure resource providers are registered.

3. Creates a VM template from OVA.

4. Creates a snapshot of the VM template created.

### `Create` command

Create command does following:

1. Deploys the appliance VM in the vCenter based on the snapshot created by `prepare` command

2. Creates an ARM resource for Arc Resource bridge representing the appliance VM it deployed.

3. Installs `azure-vmwareoperator` cluster extension on the Appliance.

4. Creates a Custom Location representing your VMWare vSphere environment.
5. Connects your VMWare vCenter to Azure Arc. This is done by creating an Azure resource representing your vCenter.

### `Delete` command

Delete command does the following operations:

1. Deletes the `azure-vmwareoperator` cluster extension.
1. Deletes the appliance VM (on your vCenter) and the Azure resource representing it.

This command is provided to create a clean slate before retrying in case of failures.

## Feedback

In case of any questions/feedback reach out to arc-vmware-feedback@microsoft.com

## Trademarks

This doc may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Any use of third-party trademarks or logos are subject to those third-party's policies.
