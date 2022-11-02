import logging

from ...entity.CustomerResource import CustomerResource
from ...entity._credentials import Credentials
from ...exception import DataNotFoundException
from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...entity.AzCli import AzCli
from ...retriever._retriever import Retriever


class ArcAddOnRetriever(Retriever):
    instance = None
    _arc_add_on_url = Constant.MGMT_URL + "addons/arc" + "?" + Constant.API_VERSION + "=" + Constant.PREVIEW_API_VERSION_VALUE
    
    def __new__(cls):
        if cls.instance is None:
            cls._az_cli_executor = AzCliExecutor()
            cls.instance = object.__new__(cls)
        return cls.instance

    def retrieve_data(self, customer_resource):
        customer_res: CustomerResource = customer_resource
        arc_add_on_url = self.arc_add_on_url.format(customer_res.subscription_id,
                                                  customer_res.resource_group,
                                                  customer_res.private_cloud)

        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u"). \
            append(arc_add_on_url)

        res = self._az_cli_executor.run_az_cli(az_cli)
        return res