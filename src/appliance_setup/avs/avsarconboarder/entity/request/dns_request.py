from dataclasses import dataclass


@dataclass
class DNSZoneRequest:
    displayName: str
    revision: int
    domain: list
    dnsServerIps: list



@dataclass
class DNSServiceRequest:
    displayName: str
    dnsServiceIp: str
    defaultDnsZone: str
    logLevel = 'INFO'
    revision = 0

