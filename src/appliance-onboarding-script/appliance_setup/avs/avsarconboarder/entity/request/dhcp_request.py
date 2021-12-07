from dataclasses import dataclass

from ...constants import Constant


@dataclass
class DHCPRequest:
    dhcpType: Constant.SERVER
    displayName: str
    serverAddress: str
    leaseTime: str
    revision:int