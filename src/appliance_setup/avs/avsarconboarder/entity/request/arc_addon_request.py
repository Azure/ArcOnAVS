from dataclasses import dataclass


@dataclass
class ArcAddonRequest:
    addonType: str
    vCenter: str

