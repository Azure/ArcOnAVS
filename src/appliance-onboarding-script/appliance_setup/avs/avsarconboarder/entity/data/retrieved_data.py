from dataclasses import dataclass

from .._credentials import Credentials
from ...entity import CustomerResource
from ...entity._vsphere_resource import VSphereResourceData


@dataclass
class CustomerDetails:
    customer_resource: CustomerResource
    vcenter_credentials: Credentials
    cloud_details: dict
    vsphere_resource_details: VSphereResourceData

