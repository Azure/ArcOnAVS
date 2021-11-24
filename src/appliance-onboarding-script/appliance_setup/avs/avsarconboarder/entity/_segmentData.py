from ..constants import Constant


##
## TODO: creating immutable class ##
##
class SegmentData:

    def __init__(self, gateway_ip_cidr, dhcp_range, name):
        self.gateway_ip_cidr = gateway_ip_cidr
        self.dhcp_range = dhcp_range
        if name is None:
            self.segment_name = Constant.SEGMENT_NAME
        else:
            self.segment_name = name
