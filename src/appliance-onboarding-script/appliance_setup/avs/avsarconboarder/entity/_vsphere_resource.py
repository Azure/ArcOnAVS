from dataclasses import dataclass


@dataclass
class VSphereResourceData:
    resourcePool: str
    folder: str
    datacenter: str
    dataStore: str
    vmTemplateName: str