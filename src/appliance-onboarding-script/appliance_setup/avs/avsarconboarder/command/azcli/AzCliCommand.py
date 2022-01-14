import json
import logging
import os
import subprocess

from ...command.Command import Command
from ...entity.AzCli import AzCli
from ...executor.Executor import Executor
from ...executor.process.process_executor import ProcessExecutor


class AzCliCommand(Command):
    def __init__(self, object: AzCli):
        if type(object) != AzCli:
            raise TypeError("not azcli object type")
        self.az_cli = object

    def execute_command(self):
        return self._az_cli_command_execute()

    def _az_cli_command_execute(self):
        try:
            result = self._execute_process(self.az_cli)
            logging.debug(result)
            # if result is not None and not empty
            if result:
                result = json.loads(result.strip())
        except Exception as e:
            print(e)
            raise e
        return result

    def _execute_process(self, az_cli):
        process_executor: Executor = ProcessExecutor(self.az_cli.build_az_cli())
        return process_executor.execute([False])
