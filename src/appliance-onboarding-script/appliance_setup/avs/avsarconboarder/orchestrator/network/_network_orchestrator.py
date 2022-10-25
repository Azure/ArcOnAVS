from ...constants import Constant
from ...orchestrator._orchestrator import Orchestrator
import ipaddress
from avs.avsarconboarder.exception import InvalidInputError

class NetworkOrchestrator(Orchestrator):

    def validate_ip_address(self, ip_addr):
        try:
            ipaddress.ip_address(ip_addr)
        except:
            raise InvalidInputError("Invalid ip addresses provided")

    def validate_static_ip_cidr_block(self, segment_ip_cidr, version):
        gateway_ip, cidr = self.get_gateway_address_cidr_from_network_addr(segment_ip_cidr)
        self.validate_ip_address(gateway_ip)
        
        if version == Constant.CONFIG_VERSION_V2:
            if int(cidr) != 28:
                raise InvalidInputError("Invalid segment block size provided, Please provide a /28 address")
            
            subnet_first_ip_addr = ipaddress.IPv4Address(gateway_ip) - 1
            try:
                ipaddress.ip_network('{}/{}'.format(subnet_first_ip_addr,cidr))
            except:
                raise InvalidInputError("Invalid gateway ip provided, please provide a segment with first gateway ip")          
        
    def get_gateway_address_cidr_from_network_addr(self, segment_ip_cidr):
        values = segment_ip_cidr.split('/')
        return values[0], values[1]

    '''
    gateway ip = 2nd ip of cidr = 10.0.0.(xxxx 0001)
    control plane IP address = 3rd ip of cidr = 10.0.0.(xxxx 0010)
    nodepool range = 11th to 15th ip = 10.0.0.(xxxx 1010) - 10.0.0.(xxxx 1110)  
    Buffer / Free IPs  = 4th to 10th Ip = 10.0.0.(xxxx 0011) - 10.0.0.(xxxx 1001)
    '''
    def populate_network_config(self, config):
        gateway_ip, cidr = self.get_gateway_address_cidr_from_network_addr(config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"])
        subnet_first_ip_addr = ipaddress.IPv4Address(gateway_ip) - 1
        list_of_ip_addr_in_segment =  list(ipaddress.ip_network('{}/{}'.format(subnet_first_ip_addr,cidr)).hosts())
        config["applianceControlPlaneIpAddress"]  = str(list_of_ip_addr_in_segment[1])
        config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"]  = str(list_of_ip_addr_in_segment[10])
        config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"] = str(list_of_ip_addr_in_segment[13])
        config["staticIpNetworkDetails"]["gatewayIPAddress"] = str(list_of_ip_addr_in_segment[0])

    def orchestrate(self, *args):
        config = args[0]
        self.populate_network_config(config)
