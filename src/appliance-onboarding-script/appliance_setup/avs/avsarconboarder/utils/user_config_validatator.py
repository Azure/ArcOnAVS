from avs.avsarconboarder.entity.CustomerResource import CustomerResource
from avs.avsarconboarder.exception import InvalidInputError
from avs.avsarconboarder.retriever.cloud_data.cloud_data_retriever import CloudDataRetriever

class ConfigValidator:
    def __init__(self, config):
        self.__config = config

    def validate_static_ip_nw_config(self):
        if "staticIpNetworkDetails" not in self.__config:
            raise InvalidInputError("staticIpNetworkDetails is a required configuration")
        if "networkForApplianceVM" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.networkForApplianceVM is a required configuration")
        if "networkCIDRForApplianceVM" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.networkCIDRForApplianceVM is a required configuration")
        if "k8sNodeIPPoolStart" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolStart is a required configuration")
        if "k8sNodeIPPoolEnd" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolEnd is a required configurations")
        if "gatewayIPAddress" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.gatewayIPAddress is a required configuration")

    def validate_dhcp_nw_config(self):
        if "DHCPNetworkDetails" not in self.__config:
            raise InvalidInputError("DHCPNetworkDetails is a required configuration")
        if "networkForApplianceVM" not in self.__config["DHCPNetworkDetails"]:
            raise InvalidInputError("DHCPNetworkDetails.networkForApplianceVM is a required configuration")
        if "networkCIDRForApplianceVM" not in self.__config["DHCPNetworkDetails"]:
            raise InvalidInputError("DHCPNetworkDetails.networkCIDRForApplianceVM is a required configuration")
        if "segmentDHCPRangeForApplianceVM" not in self.__config["DHCPNetworkDetails"]:
            raise InvalidInputError("DHCPNetworkDetails.segmentDHCPRangeForApplianceVM is a required configuration")
        if "DHCPServerCIDR" not in self.__config["DHCPNetworkDetails"]:
            raise InvalidInputError("DHCPNetworkDetails.DHCPServerCIDR is a required configuration")

    def validate_nw_config(self):

        # TODO: Once we support DHCP configuration as well, uncomment the following check for isStatic being a
        #  configuration and remove the explicit call to block DHCP configuration
        # if "isStatic" not in self.__config:
        #     raise InvalidInputError("isStatic is a required configuration")
        self.block_DHCP_config()

        if self.__config["isStatic"]:
            self.validate_static_ip_nw_config()
        else:
            self.validate_dhcp_nw_config()

    def validate_private_cloud(self):
        appliance_name = None
        if 'nameForApplianceInAzure' in self.__config:
            appliance_name = self.__config['nameForApplianceInAzure']
        customer_res: CustomerResource = CustomerResource(self.__config['resourceGroup'], self.__config['subscriptionId'],
                                                          self.__config['privateCloud'], appliance_name)
        cloud_data_retriever: CloudDataRetriever = CloudDataRetriever()
        try:
            cloud_data_retriever.retrieve_data(customer_res)
        except Exception as e:
            raise InvalidInputError(f"Invalid config, the subscriptionId, resourceGroup, privateCloud values do not "
                                    f"point to a valid privateCloud resource. The inner exception is {e}")

    def validate_azure_details(self):
        if "subscriptionId" not in self.__config:
            raise InvalidInputError("subscriptionId is a required configuration")
        if "resourceGroup" not in self.__config:
            raise InvalidInputError("resourceGroup is a required configuration")
        if "privateCloud" not in self.__config:
            raise InvalidInputError("privateCloud is a required configuration")
        self.validate_private_cloud()

    def block_DHCP_config(self):
        # Only Static IP configuration is supported currently. We raise an exception if DHCP configuration
        # is selected, i.e, if the config isStatic is false
        if "isStatic" in self.__config and not self.__config["isStatic"]:
            raise InvalidInputError("isStatic should be true. Only Static IP configuration is supported currently")

    def validate_avs_config(self):
        self.validate_nw_config()
        self.validate_azure_details()