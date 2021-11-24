from abc import abstractmethod

from ..exception import ValidationFailedException


class Processor:

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def pre_process(self):
        if not self.validate():
            raise ValidationFailedException("validation failed")
        pass

    def process(self):
        self.pre_process()
        self.execute_process()
        self.post_process()

    def post_process(self):
        pass

    @abstractmethod
    def execute_process(self):
        pass
