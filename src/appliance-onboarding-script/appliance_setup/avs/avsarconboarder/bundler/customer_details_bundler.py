from .bundler import Bundler
from ..entity.data.retrieved_data import CustomerDetails


class CustomerDetailsBundler(Bundler):

    def __init__(self):
        pass

    def bundle_data(self, *args):
        customer_res = args[0]
        customer_credentials = args[1]
        cloud_details = args[2]
        vsphere_resource = args[3]
        return CustomerDetails(customer_resource=customer_res,
                               vcenter_credentials=customer_credentials,
                               cloud_details=cloud_details, vsphere_resource_details=vsphere_resource)
