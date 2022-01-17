import logging

from ....constants import Constant
from ....entity.AzCli import AzCli
from ....entity.CustomerResource import CustomerResource
from ....entity._dnsData import DNSData
from ....executor.azcli._AzCliExecutor import AzCliExecutor


class DNSHelper:
    instance = None

    _dns_zone_url = Constant.NSX_MGMT_URL + "/dnsZones?" + Constant.API_VERSION + "=" + Constant.STABLE_API_VERSION_VALUE
    _dns_service_url = Constant.NSX_MGMT_URL + "/dnsServices?" + Constant.API_VERSION + "=" + Constant.STABLE_API_VERSION_VALUE

    def __new__(cls):
        if cls.instance is None:
            cls.az_cli_executor = AzCliExecutor()
            cls.instance = object.__new__(cls)
        return cls.instance

    def retrieve_dns_config(self, customer_resource: CustomerResource, private_cloud_details):
        logging.info("retrieving_dns_data")
        dns_zone_details = self._find_dns_zone_details(customer_resource)
        zone_details = {}
        if dns_zone_details is not None and dns_zone_details['value'] is not None and len(
                dns_zone_details['value']) > 0:
            zone_details = dns_zone_details['value'][0]
        dns_server_details = self.find_dns_server_details(customer_resource)
        server_details = {}
        if dns_server_details is not None and dns_server_details['value'] is not None and len(
                dns_server_details['value']) > 0:
            server_details = dns_server_details['value'][0]

        return DNSData(zone_details, server_details, private_cloud_details['VNET_IP_CIDR'])

    def _find_dns_zone_details(self, customer_resource):
        list_dns_zones_url = self._dns_zone_url.format(customer_resource.subscription_id,
                                                       customer_resource.resource_group,
                                                       customer_resource.private_cloud)
        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u"). \
            append(list_dns_zones_url)
        return self.az_cli_executor.run_az_cli(az_cli)

    def find_dns_server_details(self, customer_resource):
        list_dns_server_url = self._dns_service_url.format(customer_resource.subscription_id,
                                                           customer_resource.resource_group,
                                                           customer_resource.private_cloud)
        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u"). \
            append(list_dns_server_url)
        return self.az_cli_executor.run_az_cli(az_cli)