import enum

class CreatorType(enum.Enum):
    dhcp = 0
    segment = 1
    file = 4
    dns_zone = 5
    dns_service = 6