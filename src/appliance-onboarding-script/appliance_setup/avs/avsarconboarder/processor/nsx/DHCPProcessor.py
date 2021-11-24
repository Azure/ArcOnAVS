from _ast import Constant

from ...constants import Constant
from ...creator.type.creator_type import CreatorType
from ...entity.CustomerResource import CustomerResource
from ...entity._dhcpData import DHCPData
from ...entity.request.dhcp_request import DHCPRequest
from ...exception import AlreadyExistsException
from ...factory.creator import creator
from ...processor._processor import Processor
from ...processor.nsx.helper._DHCPHelper import DHCPHelper


class DHCPProcessor(Processor):

    def __init__(self, customer_res: CustomerResource, dhcp_data: DHCPData):
        self.customer_res = customer_res
        self.dhcp_helper = DHCPHelper()
        self.dhcp_data = dhcp_data
        self.dhcp_creator = creator.get_instance().retrieve_instance([CreatorType.dhcp])

    def validate(self):
        if self._dhcp_server_count >= 1:
            print("dhcp creation is not required it already exists")
            raise AlreadyExistsException('DHCP already enabled')
        return True

    def pre_process(self):
        dhcp_server_list = self.dhcp_helper.retrieve_dhcp_server(self.customer_res.subscription_id,
                                                                 self.customer_res.resource_group,
                                                                 self.customer_res.private_cloud)
        self._dhcp_server_count = self.dhcp_helper.find_dhcp_server_count(dhcp_server_list)

        Processor.pre_process(self)

    def execute_process(self):
        dhcp_request = DHCPRequest(dhcpType=Constant.SERVER,
                                   displayName=Constant.DHCP_NAME,
                                   serverAddress=self.dhcp_data.ip_cidr,
                                   leaseTime=None,
                                   revision=0)
        res = self.dhcp_creator.create([self.customer_res, dhcp_request])
        print("res for create DHCP -- ", res)
        pass
