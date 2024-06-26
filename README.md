# Helper script for enabling ARC on Azure VMware Solution

This helper script is provided to help you simplify the onboarding to ARC on Azure VMware Solution.

## Arc on AVS public doc

Please follow the [documentation](https://learn.microsoft.com/en-us/azure/azure-vmware/deploy-arc-for-azure-vmware-solution?tabs=windows) to use the script and deploy Arc for Azure VMware Solution

## Using the script

### On a Windows machine

Open a PowerShell window and run the following command. You will need to bypass execution policy as the script is not signed.
As with any script downloaded from the internet, do read its contents before running it.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\run.ps1 -Operation onboard -FilePath <path_to_config_avs.json>
```
You can additionally specify the log level as debug to get DEBUG level logs.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\run.ps1 -Operation onboard -FilePath <path_to_config_avs.json> -LogLevel DEBUG
```

### On a Linux machine

Use commands as follows:

```bash
sudo chmod +x run.sh 
sudo bash run.sh onboard <path_to_config_avs.json>
```
You can additionally specify the log level as debug to get DEBUG level logs.

```bash
sudo chmod +x run.sh
sudo bash run.sh onboard <path_to_config_avs.json> DEBUG
```

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
