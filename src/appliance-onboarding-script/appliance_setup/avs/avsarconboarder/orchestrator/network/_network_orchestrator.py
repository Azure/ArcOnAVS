from ...orchestrator._orchestrator import Orchestrator
import ipaddress
from avs.avsarconboarder.exception import InvalidInputError

class NetworkOrchestrator(Orchestrator):
    def __init__(self):
        self.list_of_ip_addr_in_segment = list()

    def validate_static_ip_cidr_block(self, config):
        segmant_ip_cidr = config["staticIpNetworkDetails"]["networkCIDRForApplianceVM"]
        gateway_ip      = ""
        char_index      = 0
        while char_index < len(segmant_ip_cidr) and segmant_ip_cidr[char_index] != '/':
            gateway_ip += segmant_ip_cidr[char_index]
            char_index += 1

        cidr = segmant_ip_cidr[char_index - len(segmant_ip_cidr) + 1:]
        if int(cidr) != 28:
            raise InvalidInputError("Invalid segamnt block size provided, Please provide a /28 address")
        
        try:
            subnet_first_ip_addr = ipaddress.IPv4Address(gateway_ip) - 1
            self.list_of_ip_addr_in_segment = list(ipaddress.ip_network('{}/{}'.format(subnet_first_ip_addr,cidr)).hosts())
        except:
            raise InvalidInputError("Invalid gateway ip provided, please provide a segmant with first gateway ip")          
    
    def populate_network_config(self, config):
        print(self.list_of_ip_addr_in_segment)
        config["applianceControlPlaneIpAddress"]  = str(self.list_of_ip_addr_in_segment[1])
        config["staticIpNetworkDetails"]["k8sNodeIPPoolStart"]  = str(self.list_of_ip_addr_in_segment[10])
        config["staticIpNetworkDetails"]["k8sNodeIPPoolEnd"] = str(self.list_of_ip_addr_in_segment[13])
        config["staticIpNetworkDetails"]["gatewayIPAddress"] = str(self.list_of_ip_addr_in_segment[0])

    def orchestrate(self, *args):
        config = args[0]
        self.validate_static_ip_cidr_block(config)
        self.populate_network_config(config)
