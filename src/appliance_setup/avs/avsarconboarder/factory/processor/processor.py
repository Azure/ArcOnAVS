from ...exception import UnexpectedRetrievalException
from ...factory.absfact import ArcAbsFactory
from ...processor import _processor
from ...processor.nsx.DHCPProcessor import DHCPProcessor
from ...processor.nsx.SegmentProcessor import SegmentProcessor
from ...processor.nsx._dns_processor import DNSProcessor
from ...processor.type._ProcessorType import ProcessorType


class ProcessorFactory(ArcAbsFactory):
    _instance_map = {}

    def retrieve_instance(self, *args): #type :ProcessorType):
        type: ProcessorType = args[0]
        if self._instance_map[type] is not None:
            return self._instance_map[type]
        raise UnexpectedRetrievalException("processor type is not found")

    def build_factory(self, *args):
        processor_type = args[2]
        customer_res = args[0]
        process_specific_res = args[1]
        processor: _processor = None
        if processor_type == ProcessorType.dhcp:
            processor = DHCPProcessor(customer_res, process_specific_res)
        elif processor_type == ProcessorType.segment:
            processor = SegmentProcessor(customer_res, process_specific_res)
        elif processor_type == ProcessorType.dns:
            processor = DNSProcessor(customer_res, process_specific_res)

        self._instance_map[processor_type] = processor


factory_instance = None


def get_instance():
    if factory_instance is None:
        instance = ProcessorFactory()
    return instance