from ...creator.type.creator_type import CreatorType
from ...entity.CustomerResource import CustomerResource
from ...entity._dnsData import DNSData
from ...exception import AlreadyExistsException
from ...factory.creator import creator
from ...processor._processor import Processor
from ...processor.nsx.helper._DNSHelper import DNSHelper


class DNSProcessor(Processor):

    def __init__(self, customer_res: CustomerResource, private_cloud_details):
        self.customer_res = customer_res
        self.dns_zone_creator = creator.get_instance().retrieve_instance([CreatorType.dns_zone])
        self.dns_service_creator = creator.get_instance().retrieve_instance([CreatorType.dns_service])
        self.dns_helper = DNSHelper()
        self.private_cloud_details = private_cloud_details

    def validate(self):
        if len(self.dns_data.zone_details) > 0 and len(self.dns_data.server_details) > 0:
            raise AlreadyExistsException("dns zone creation and server creation both are not required it already exists")
        return True

    def pre_process(self):
        self.dns_data: DNSData = self.dns_helper.retrieve_dns_config(self.customer_res, self.private_cloud_details)
        Processor.pre_process(self)

    def execute_process(self):
        if len(self.dns_data.zone_details) == 0:
            self.dns_zone_creator.create(self.customer_res)

        if len(self.dns_data.server_details) == 0:
            self.dns_service_creator.create(self.customer_res, self.dns_data)

        pass
