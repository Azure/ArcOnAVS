import logging

from ...entity.CustomerResource import CustomerResource
from ...entity._credentials import Credentials
from ...exception import DataNotFoundException
from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...entity.AzCli import AzCli
from ...retriever._retriever import Retriever


class CredentialsRetriever(Retriever):
    instance = None
    _credential_url = Constant.MGMT_URL+"listAdminCredentials?"+Constant.API_VERSION+"="+Constant.MGMT_API_VERSION_VALUE

    def __new__(cls):
        if cls.instance is None:
            cls._az_cli_executor = AzCliExecutor()
            cls.instance = object.__new__(cls)

        return cls.instance

    def retrieve_data(self, object):
        customer_resource: CustomerResource = object
        logging.info("retrieve_data :: CredentialsRetriever")
        credential_url = self._credential_url.format(customer_resource.subscription_id, customer_resource.resource_group,
                                    customer_resource.private_cloud)
        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.POST).append("-u").\
            append(credential_url)
        res = self._az_cli_executor.run_az_cli(az_cli)
        logging.info("customer credentials retrieved")
        return self._build_vmware_credentials(res)

    def _build_vmware_credentials(self, res):
        if 'vcenterUsername' not in res or res['vcenterUsername'] == '':
            raise DataNotFoundException('vcenter username not found')
        if 'vcenterPassword' not in res or res['vcenterPassword'] == '':
            raise DataNotFoundException('vcenter password not found')

        return Credentials(username=res['vcenterUsername'], password=res['vcenterPassword'])