import os


class TempChangeDir(object):
    def __init__(self, dir) -> None:
        self._prev = os.getcwd()
        self._new = dir

    def __enter__(self):
        os.chdir(self._new)

    def __exit__(self, *args, **kwargs):
        os.chdir(self._prev)