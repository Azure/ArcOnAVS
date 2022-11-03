import json
import os
import tempfile
from pathlib import Path

from ...creator.creator import Creator


class FileCreator(Creator):

    def create(self, *args):
        file_name, file_path, is_temp_path, json_obj = self._retrieve_data(args)
        file_dir_path = self._find_dir(file_path, is_temp_path)
        file_path = self._process_file_writing(file_dir_path, file_name, file_path, json_obj)

        return file_path

    def _process_file_writing(self, file_dir_path, file_name, file_path, json_obj):
        file_path = file_dir_path + os.sep + file_name
        self._check_if_file_exists_remove(file_path)
        data = json.dumps(json_obj, default=lambda o: o.__dict__)
        self._write_in_file(data, file_path)
        return file_path

    def _write_in_file(self, data, file_path):
        with open(file_path, "w") as fp:
            fp.write(data)

    def _retrieve_data(self, args):
        json_obj = args[0][0]
        file_name = args[0][1]
        is_temp_path = args[0][2]
        file_path = args[0][3]
        return file_name, file_path, is_temp_path, json_obj

    def _find_dir(self, file_path, is_temp_path):
        file_dir_path = None
        if is_temp_path:
            file_dir_path = tempfile.gettempdir()
        elif file_path is not None or file_path == "":
            file_dir_path = file_path
        else:
            file_dir_path = ""

        return file_dir_path

    def _check_if_file_exists_remove(self, file_path):
        file = Path(file_path)
        if not file.is_file():
            return
        os.remove(file_path)