from ...entity._dhcpData import DHCPData
from ...entity._segmentData import SegmentData
from ...entity.data.retrieved_data import CustomerDetails
from ...factory import absfact
from ...factory.absfact import ArcAbsFactory
from ...factory.processor.processor import ProcessorFactory
from ...orchestrator.event._event_orchestrator import EventOrchestrator
from ...exception import ValidationFailedException, AlreadyExistsException
from ...orchestrator._orchestrator import Orchestrator
from ...processor.type._ProcessorType import ProcessorType


class NSXOrchestor(Orchestrator):

    def __init__(self, customer_details: CustomerDetails, dhcp_data:DHCPData, segment_data: SegmentData):
        self.customer_details = customer_details
        self.dhcp_data = dhcp_data
        self.segment_data = segment_data
        self._event_orchestrator = EventOrchestrator()
        self._processor_factory: ArcAbsFactory = ProcessorFactory()


    def orchestrate(self, *args):
        self._build_processors(self.customer_details, self.dhcp_data, self.segment_data)
        self._orchestrate_nsx_events()

    def _build_processors(self, customer_details: CustomerDetails, dhcp_data: DHCPData, segment_data: SegmentData):
        if self.dhcp_data is not None:
            self._processor_factory.build_factory(customer_details.customer_resource, dhcp_data, ProcessorType.dhcp)
        self._processor_factory.build_factory(customer_details.customer_resource, segment_data, ProcessorType.segment)
        self._processor_factory.build_factory(customer_details.customer_resource, customer_details.cloud_details, ProcessorType.dns)

    def _orchestrate_nsx_events(self):

        if self.dhcp_data is not None:
            try:
                self._event_orchestrator.orchestrate(ProcessorType.dhcp)
            except AlreadyExistsException as aee:
                print(aee.args[0])
        try:
            self._event_orchestrator.orchestrate(ProcessorType.segment)
        except AlreadyExistsException as aee:
            print(aee.args[0])

        try:
            self._event_orchestrator.orchestrate(ProcessorType.dns)
        except AlreadyExistsException as aee:
            print(aee.args[0])

        return
