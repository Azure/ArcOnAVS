from operator import truediv
from avs.avsarconboarder.entity.CustomerResource import CustomerResource
from avs.avsarconboarder.orchestrator.network._network_orchestrator import NetworkOrchestrator
from avs.avsarconboarder.exception import InvalidInputError
from avs.avsarconboarder.retriever.cloud_data.cloud_data_retriever import CloudDataRetriever
from avs.avsarconboarder.constants import Constant
from ..processor.nsx.helper import _NSXSegmentHelper

class ConfigValidator:
    def __init__(self, config):
        self.__config = config
        self._network_orchestrator = NetworkOrchestrator()
        self._segment_helper = _NSXSegmentHelper.NSXSegmentHelper()
        
    def validate_static_ip_nw_config_v1(self):
        self._network_orchestrator.validate_ip_address(self.__config["applianceControlPlaneIpAddress"])
        self._network_orchestrator.validate_static_ip_cidr_block(self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"], Constant.CONFIG_VERSION_V1)
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"])
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"])
        self._network_orchestrator.validate_ip_address(self.__config["staticIpNetworkDetails"]["gatewayIPAddress"])
        
        gateway_ip_cidr = self._network_orchestrator.get_gateway_address_cidr_from_network_addr(self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"])
        if gateway_ip_cidr[0] != self.__config["staticIpNetworkDetails"]["gatewayIPAddress"]:
            raise InvalidInputError("Gateway IP in config and gateway of segment do not match")

    def validate_static_ip_nw_config_v2(self):
        self._network_orchestrator.validate_static_ip_cidr_block(self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"], Constant.CONFIG_VERSION_V2)
 
    def validate_static_ip_nw_config(self):
        if "applianceControlPlaneIpAddress" not in self.__config:
            raise InvalidInputError("applianceControlPlaneIpAddress is a required configuration")    
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

        config_version = self.get_config_version()
        if config_version == Constant.CONFIG_VERSION_V1:
            self.validate_static_ip_nw_config_v1()
        elif config_version == Constant.CONFIG_VERSION_V2:
            self.validate_static_ip_nw_config_v2()
        
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

    #checks if all the fields in config are present
    def check_if_nw_config_v1(self):
        if not self.__config["applianceControlPlaneIpAddress"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["networkForApplianceVM"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["gatewayIPAddress"].strip():
            return False
        return True

    #checks if only networkForApplianceVM and networkCIDRForApplianceVM are present in config
    def check_if_nw_config_v2(self):
        if self.__config["applianceControlPlaneIpAddress"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["networkForApplianceVM"].strip():
            return False
        if not self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"].strip():
            return False
        if self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"].strip():
            return False
        if self.__config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"].strip():
            return False
        if self.__config["staticIpNetworkDetails"]["gatewayIPAddress"].strip():
            return False
        return True

    def get_config_version(self):
        if(self.check_if_nw_config_v1()):
            return Constant.CONFIG_VERSION_V1
        if(self.check_if_nw_config_v2()):
            return Constant.CONFIG_VERSION_V2
        raise InvalidInputError("The Config file does not qualify for either of versions. Please provide the fields according to documentation.")
    
    '''
    Checks if the segment details given by the user in config matches with the segments present in the sddc.
    '''
    def validate_segment_details_config(self):
        res = self._segment_helper.get_segment_list(self.__config['subscriptionId'], 
                                                    self.__config['resourceGroup'], self.__config['privateCloud'])
        
        segment_in_config = self.__config["staticIpNetworkDetails"]["networkForApplianceVM"]
        segment_cidr_in_config = self.__config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"]
        for segment in res["value"]:
            if segment["name"].casefold() == segment_in_config.casefold():
                if segment["properties"]["subnet"]["gatewayAddress"] != segment_cidr_in_config:
                    raise InvalidInputError("Segment {} already exists with a different gateway ip cidr".format(segment_in_config))

        for segment in res["value"]:
            if segment["properties"]["subnet"]["gatewayAddress"] == segment_cidr_in_config:
                if segment["name"].casefold() != segment_in_config.casefold():
                    raise InvalidInputError("A different segment already present with gateway ip cidr {}".format(segment_cidr_in_config))
     
    def validate_avs_config(self):
        self.validate_nw_config()
        self.validate_azure_details()
        self.validate_segment_details_config()