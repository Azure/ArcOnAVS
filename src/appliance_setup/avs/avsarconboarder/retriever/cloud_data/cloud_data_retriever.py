import logging

from ...entity.CustomerResource import CustomerResource
from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...entity.AzCli import AzCli
from ...retriever._retriever import Retriever

from ...retriever.cloud_data.helper.cloud_data_helper import CloudDataHelper


class CloudDataRetriever(Retriever):
    instance = None
    _cloud_details_url = Constant.MGMT_URL + "?" + Constant.API_VERSION + "=" + Constant.MGMT_API_VERSION_VALUE

    def __new__(cls):
        if cls.instance is None:
            cls._az_cli_executor = AzCliExecutor()
            cls.instance = object.__new__(cls)

        return cls.instance

    def retrieve_data(self, object):
        logging.info("retrieve_data")
        customer_resource: CustomerResource = object
        cloud_details_url = self._cloud_details_url.format(customer_resource.subscription_id,
                                                               customer_resource.resource_group,
                                                               customer_resource.private_cloud)

        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u"). \
            append(cloud_details_url)
        cloud_data = {}
        res = self._az_cli_executor.run_az_cli(az_cli)
        return self._build_cloud_data(cloud_data, res)

    def _build_cloud_data(self, cloud_data, res):
        cloud_data_helper = CloudDataHelper(res)
        cloud_data[Constant.LOCATION] = cloud_data_helper.find_cluster_location()
        cloud_data[Constant.VCSA_END_POINT] = cloud_data_helper.get_vcsa_endpoint()
        cloud_data[Constant.INTERNET] = cloud_data_helper.find_internet_enabled()
        cloud_data[Constant.PROVISIONING_STATE], cloud_data[Constant.CLUSTER_SIZE] = cloud_data_helper. \
            find_provisioning_state_cluster_size()
        cloud_data[Constant.VNET_IP_CIDR] = cloud_data_helper.find_vnet_ip_cidr()
        logging.info("customer cloud details retrieved")
        return cloud_data