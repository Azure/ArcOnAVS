
from ...command.azcli.AzCliCommand import AzCliCommand
from ...executor.Executor import Executor
from ...executor.azcli.command.AzCliCommandExecutor import AzCliCommandExecutor


class AzCliExecutor(Executor):

    def __init__(self):
        pass

    def run_az_cli(self, *args):
        az_cli = args[0]
        az_cli_command = AzCliCommand(az_cli)
        az_cli_cmd_executor = AzCliCommandExecutor(az_cli_command)
        return az_cli_cmd_executor.execute()