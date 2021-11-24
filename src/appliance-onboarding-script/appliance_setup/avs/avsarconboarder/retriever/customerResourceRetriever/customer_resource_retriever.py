from ...constants import Constant
from ...entity.CustomerResource import CustomerResource
from ...retriever._retriever import Retriever


class CustomerResourceRetriever(Retriever):
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)

        return cls.instance

    def retrieve_data(self, customer_resource):
        print("retrieve_data :: ", self.__class__)
        return CustomerResource(customer_resource[Constant.RESOURCE_GROUP], customer_resource[Constant.SUBSCRIPTION_ID],
                                customer_resource[Constant.PRIVATE_CLOUD_NAME], customer_resource['region'],
                                customer_resource[Constant.APPLIANCE_NAME])
