import json
import logging
import sys

from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...creator.creator import Creator
from ...entity.AzCli import AzCli
from ...exception import DHCPCreationException
from ...entity.CustomerResource import CustomerResource
from ...entity.request.dhcp_request import DHCPRequest


class DHCPCreator(Creator):
    _create_dhcp = Constant.NSX_SUBSCRIPTION_URI + "/dhcpConfigurations/{3}"

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()

    def create(self, *args):
        customer_res: CustomerResource = args[0][0]
        dhcp_data: DHCPRequest = args[0][1]
        create_dhcp_uri = self._create_dhcp.format(customer_res.subscription_id, customer_res.resource_group,
                                                   customer_res.private_cloud, dhcp_data.displayName)
        json_data = json.dumps(json.dumps(dhcp_data.__dict__))
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_dhcp_uri).append("--properties").append(json_data) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.STABLE_API_VERSION_VALUE)

        # Adding explicit get call to work around ongoing issue where
        # Az CLI put calls do not return the complete resource payload
        get_az_cli = AzCli().append(Constant.RESOURCE).append(Constant.GET).append("--id") \
            .append(create_dhcp_uri)
        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            logging.info("Created DHCP server")
            res = self._az_cli_executor.run_az_cli(get_az_cli)
        except Exception as e:
            raise DHCPCreationException("Exception occured while creating DHCP server!") from e
        return res
