import json
import logging
import sys
import ipaddress
import time
from ipaddress import IPv4Address

from ...entity._dnsData import DNSData
from ...entity.request.dns_request import DNSZoneRequest, DNSServiceRequest
from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...creator.creator import Creator
from ...entity.AzCli import AzCli
from ...exception import DNSZoneCreationException, DNSServerCreationException
from ...entity.CustomerResource import CustomerResource
from ...processor.nsx.helper._DNSHelper import DNSHelper


class DNSZoneCreator(Creator):
    _create_dns_zones_uri = Constant.NSX_SUBSCRIPTION_URI + "/dnsZones/{3}"

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()

    def create(self, *args):
        customer_res: CustomerResource = args[0]
        create_dns_zone = self._create_dns_zones_uri.format(customer_res.subscription_id,
                                                            customer_res.resource_group,
                                                            customer_res.private_cloud, 'default')
        json_data = json.dumps(json.dumps(self._create_dns_zone_payload()))
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_dns_zone).append("--properties").append(json_data) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.STABLE_API_VERSION_VALUE) \
            .append("--debug")
        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            print("response for create dns zone :: ", res)
        except Exception as e:
            raise DNSZoneCreationException("Exception occured while creating dns zone!") from e
        return res

    def _create_dns_zone_payload(self):
        dns_zone_req = DNSZoneRequest(displayName='default', domain=[], dnsServerIps=["1.1.1.1", "1.0.0.1"],
                                      revision=0)
        return dns_zone_req.__dict__


class DNSServiceCreator(Creator):
    _create_dns_service_uri = Constant.NSX_SUBSCRIPTION_URI + "/dnsServices/{3}"
    _dns_service_name = 'arc-dns'

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()
        self._dns_helper = DNSHelper()

    def create(self, *args):
        self._customer_res: CustomerResource = args[0]
        dns_data: DNSData = args[1]
        create_dns_service = self._create_dns_service_uri.format(self._customer_res.subscription_id,
                                                                 self._customer_res.resource_group,
                                                                 self._customer_res.private_cloud, 'arc-dns')
        json_data = json.dumps(json.dumps(self._create_dns_service_payload(self._customer_res, dns_data)))
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_dns_service).append("--properties").append(json_data) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.STABLE_API_VERSION_VALUE).append("--debug")

        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            logging.info("response for create dns service :: ", res)
        except Exception as e:
            time.sleep(60)
            dns_server_details = self._dns_helper.find_dns_server_details(self._customer_res)
            if dns_server_details is not None and dns_server_details['value'] is not None and len(
                    dns_server_details['value']) == 1:
                logging.info('dns server created')
                return
            raise DNSServerCreationException("Exception occured while creating dns server!") from e
        return res

    def _create_dns_service_payload(self, customer_res: CustomerResource, dns_data: DNSData):
        dns_ip_cidr = dns_data.vnet_ip_cidr
        ip_addr = dns_ip_cidr.split('/')
        vnet_ip_add: IPv4Address = ipaddress.ip_address(ip_addr[0])
        vnet_ip_add = vnet_ip_add + 192
        dns_service_payload = DNSServiceRequest(displayName=self._dns_service_name, dnsServiceIp=str(vnet_ip_add),
                                                defaultDnsZone='default')

        return dns_service_payload.__dict__
