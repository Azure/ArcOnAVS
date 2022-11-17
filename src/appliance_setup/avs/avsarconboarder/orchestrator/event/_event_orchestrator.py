from pip._internal.resolution.resolvelib import factory

from ...factory.processor.processor import ProcessorFactory
from ...orchestrator._orchestrator import Orchestrator
from ...processor._processor import Processor
from ...processor.type._ProcessorType import ProcessorType


class EventOrchestrator(Orchestrator):

    def __init__(self):
        self.process_factory : factory = ProcessorFactory()

    def orchestrate(self, *args):
        event: ProcessorType = args[0]
        processor : Processor = self.process_factory.retrieve_instance(event)
        processor.process()