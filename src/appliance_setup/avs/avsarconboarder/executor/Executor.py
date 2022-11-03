import abc


class Executor:

    @abc.abstractmethod
    def execute(self, *args):
        pass