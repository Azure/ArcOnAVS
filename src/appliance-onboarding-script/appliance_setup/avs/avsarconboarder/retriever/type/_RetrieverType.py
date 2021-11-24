import enum


class RetrieverType(enum.Enum):
    customer_resource = 0
    dhcp_data = 1
    segment_data = 2
    customer_credentials = 3
    cloud_details = 4
    vsphere_resource = 5
    dns_data = 6