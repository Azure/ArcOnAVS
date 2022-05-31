import logging
import os
import subprocess
import tempfile


from ...executor.Executor import Executor
from ...utils.utils import bytes_to_string


class ProcessExecutor(Executor):

    def __init__(self, object: str):
        self._process_cmd = object

    def execute(self, *args):
        dump_log: bool = args[0][0]
        if dump_log:
            log_path = tempfile.gettempdir() + os.sep + "output.log"
            with open(log_path, 'w') as fp:
                pass
            process_cmd = self._process_cmd+" >> "+log_path
            logging.info(self._process_cmd+" >> "+log_path)
        else:
            process_cmd = self._process_cmd
        try:
            output = subprocess.check_output(process_cmd, timeout=100000, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(bytes_to_string(e.output))
            return None
        result = bytes_to_string(output)

        return result