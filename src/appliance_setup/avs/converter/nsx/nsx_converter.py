from .._converter import Converter
from ...avsarconboarder.entity._dhcpData import DHCPData
from ...avsarconboarder.entity._segmentData import SegmentData


class DHCPConverter(Converter):

    def convert_data(self, *args):
        config = args[0]
        if config["isStatic"]:
            return None
        return DHCPData(config['DHCPNetworkDetails']['DHCPServerCIDR'])


class SegmentConverter(Converter):

    def convert_data(self, *args):
        config = args[0]
        if config["isStatic"]:
            name = config['staticIpNetworkDetails']['networkForApplianceVM']
            gateway_ip_cidr = config['staticIpNetworkDetails']['networkCIDRForApplianceVM']
            dhcp_range = []
        else:
            name = config['DHCPNetworkDetails']['networkForApplianceVM']
            gateway_ip_cidr = config['DHCPNetworkDetails']['networkCIDRForApplianceVM']
            dhcp_range = [config['DHCPNetworkDetails']['segmentDHCPRangeForApplianceVM']]
        return SegmentData(gateway_ip_cidr, dhcp_range, name)
