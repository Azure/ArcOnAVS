from ...exception import UnexpectedRetrievalException
from ...factory.absfact import ArcAbsFactory
from ...retriever import _retriever
from ...retriever.cloud_data.cloud_data_retriever import CloudDataRetriever
from ...retriever.credentials.credential_retriever import CredentialsRetriever
from ...retriever.customerResourceRetriever.customer_resource_retriever import CustomerResourceRetriever
from ...retriever.type._RetrieverType import RetrieverType
from ...retriever.vsphere.vsphere_details_retriever import VSphereDetails


class RetrieverFactory(ArcAbsFactory):
    instance_map = {}

    def retrieve_instance(self, *args):
        retriever_type = args[0][0]
        if self.instance_map[retriever_type] is not None:
            return self.instance_map[retriever_type]
        raise UnexpectedRetrievalException("retrieval type is not found")

    def build_factory(self, *args):
        for retriever_type in RetrieverType:
            retriever: _retriever = None
            if retriever_type == RetrieverType.customer_resource:
                retriever = CustomerResourceRetriever()
            elif retriever_type == RetrieverType.customer_credentials:
                retriever = CredentialsRetriever()
            elif retriever_type == RetrieverType.cloud_details:
                retriever = CloudDataRetriever()
            elif retriever_type == RetrieverType.vsphere_resource:
                retriever = VSphereDetails()

            self.instance_map[retriever_type] = retriever


factory_instance = None


def get_instance():
    if factory_instance is None:
        instance = RetrieverFactory()
        instance.build_factory()
    return instance
