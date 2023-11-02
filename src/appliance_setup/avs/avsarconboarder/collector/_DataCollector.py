from ..bundler.bundler import Bundler
from ..bundler.customer_details_bundler import CustomerDetailsBundler
from ..collector.collector import Collector
from ..entity.CustomerResource import CustomerResource
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
        cloud_details, customer_credentials = self._collect_customer_cloud_data(customer_res)
        vsphere_resource = self._vsphere_resource_retriever.retrieve_data(cloud_details, customer_credentials)
        return self.customer_details_bundler.bundle_data(customer_res, customer_credentials, cloud_details,
                                                         vsphere_resource)

    def _collect_customer_cloud_data(self, customer_res):
        customer_credentials = self.credentials_retriever.retrieve_data(customer_res)
        cloud_details = self.cloud_details_retriever.retrieve_data(customer_res)
        return cloud_details, customer_credentials
