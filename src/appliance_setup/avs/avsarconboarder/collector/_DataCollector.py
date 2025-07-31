import logging

from ..bundler.bundler import Bundler
from ..bundler.customer_details_bundler import CustomerDetailsBundler
from ..collector.collector import Collector
from ..entity.CustomerResource import CustomerResource
from ..entity._credentials import Credentials
from ..factory import retriever
from ..factory.retriever import retriever
from ..retriever import _retriever
from ..retriever.type._RetrieverType import RetrieverType


class DataCollector(Collector):

    def __init__(self):
        _retrieval_factory = retriever.get_instance()
        self._customer_res_retriever: _retriever = _retrieval_factory.retrieve_instance([RetrieverType.customer_resource])
        self._build_customer_cloud_retriever(_retrieval_factory)
        self.customer_details_bundler: Bundler = CustomerDetailsBundler()
        self._vsphere_resource_retriever: _retriever = _retrieval_factory.retrieve_instance([RetrieverType.vsphere_resource])

    def _build_customer_cloud_retriever(self, retrieval_factory):
        self.credentials_retriever: _retriever = retrieval_factory.retrieve_instance(
            [RetrieverType.customer_credentials])
        self.cloud_details_retriever: _retriever = retrieval_factory.retrieve_instance([RetrieverType.cloud_details])

    def collect_data(self, *args):
        customer_res: CustomerResource = args[0]
        config = args[1]
        cloud_details = self._collect_customer_cloud_data(customer_res)
        customer_credentials = self._collect_customer_credentials(customer_res, config)
        vsphere_resource = self._vsphere_resource_retriever.retrieve_data(cloud_details, customer_credentials)
        return self.customer_details_bundler.bundle_data(customer_res, customer_credentials, cloud_details,
                                                         vsphere_resource)

    def _collect_customer_credentials(self, customer_res, config):
        if(config["applianceCredentials"]):
            if(config["applianceCredentials"]["username"].strip() != "" or
               config["applianceCredentials"]["password"].strip() != ""):
                logging.info(f"Custom Credentials are provided in config file. "
                             f"Using username: {config['applianceCredentials']['username']}.")
                customer_credentials = Credentials(username=config['applianceCredentials']['username'],
                                   password=config['applianceCredentials']['password'])
                return customer_credentials
            
        logging.info("Custom Credentials are not provided in config file. "
                    "Using cloudAdmin for vCenter.")
        customer_credentials = self.credentials_retriever.retrieve_data(customer_res)
        return customer_credentials
        
    def _collect_customer_cloud_data(self, customer_res):
        cloud_details = self.cloud_details_retriever.retrieve_data(customer_res)
        return cloud_details
