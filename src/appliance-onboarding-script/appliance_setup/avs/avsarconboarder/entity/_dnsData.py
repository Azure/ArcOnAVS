from dataclasses import dataclass


class DNSData:
    zone_details: {}
    server_details: {}
    vnet_ip_cidr: str

    def __init__(self, zone_details, server_details, vnet_ip_cdr):
        self.zone_details = zone_details
        self.server_details = server_details
        self.vnet_ip_cidr = vnet_ip_cdr
