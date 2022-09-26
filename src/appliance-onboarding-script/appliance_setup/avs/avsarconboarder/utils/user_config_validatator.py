from operator import truediv
from avs.avsarconboarder.entity.CustomerResource import CustomerResource
from avs.avsarconboarder.orchestrator.network._network_orchestrator import NetworkOrchestrator
from avs.avsarconboarder.exception import InvalidInputError
from avs.avsarconboarder.retriever.cloud_data.cloud_data_retriever import CloudDataRetriever
import ipaddress
from avs.avsarconboarder.constants import Constant

class ConfigValidator:
    def __init__(self, config):
        self.__config = config
        self._network_orchestrator = NetworkOrchestrator()

    def validate_old_version_static_ip_nw_config(self):
        self._network_orchestrator.validate_ip_address(self.__config["applianceControlPlaneIpAddress"])
        self._network_orchestrator.validate_static_ip_cidr_block(self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"], Constant.OLD_CONFIG_VERSION)
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"])
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"])
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["gatewayIPAddress"])

    def validate_new_version_static_ip_nw_config(self):
        if self.__config["applianceControlPlaneIpAddress"].strip():
            raise InvalidInputError("applianceControlPlaneIpAddress value should be empty in new config")
        if self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"].strip():
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolStart value should should be empty in new config")
        if self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"].strip():
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolEnd value should be empty in new config")    
        if self.__config["staticIpNetworkDetails"]["gatewayIPAddress"].strip():
            raise InvalidInputError("staticIpNetworkDetails.gatewayIPAddress value should be empty in new config")
        self._network_orchestrator.validate_static_ip_cidr_block(self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"], Constant.NEW_CONFIG_VERSION)
        
    def validate_static_ip_nw_config(self):
        if "applianceControlPlaneIpAddress" not in self.__config:
            raise InvalidInputError("applianceControlPlaneIpAddress is a required configuration")    
        if "staticIpNetworkDetails" not in self.__config:
            raise InvalidInputError("staticIpNetworkDetails is a required configuration")

        if "networkForApplianceVM" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.networkForApplianceVM is a required configuration")
        else:
            if not self.__config["staticIpNetworkDetails"]["networkForApplianceVM"].strip():
                raise InvalidInputError("staticIpNetworkDetails.networkForApplianceVM is empty")

        if "networkCIDRForApplianceVM" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.networkCIDRForApplianceVM is a required configuration")
        if "k8sNodeIPPoolStart" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolStart is a required configuration")
        if "k8sNodeIPPoolEnd" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.k8sNodeIPPoolEnd is a required configurations")
        if "gatewayIPAddress" not in self.__config["staticIpNetworkDetails"]:
            raise InvalidInputError("staticIpNetworkDetails.gatewayIPAddress is a required configuration")
        
        if self.__config["applianceControlPlaneIpAddress"].strip():
            self.validate_old_version_static_ip_nw_config()
        else:
            self.validate_new_version_static_ip_nw_config()
        
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

    def get_config_version(self):
        if self.__config["applianceControlPlaneIpAddress"].strip():
            return Constant.OLD_CONFIG_VERSION
        return Constant.NEW_CONFIG_VERSION

    def validate_avs_config(self):
        self.validate_nw_config()
        self.validate_azure_details()