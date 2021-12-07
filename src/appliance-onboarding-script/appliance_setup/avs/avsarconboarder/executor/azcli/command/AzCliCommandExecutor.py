from ....command.azcli.AzCliCommand import AzCliCommand
from ....executor.Executor import Executor


class AzCliCommandExecutor(Executor):

    def __init__(self, object: AzCliCommand):
        self.az_cli_command = object

    def execute(self, *args):
        return self.az_cli_command.execute_command()