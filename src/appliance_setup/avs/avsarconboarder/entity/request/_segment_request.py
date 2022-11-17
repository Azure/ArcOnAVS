from dataclasses import dataclass


@dataclass
class SegmentRequest:

    displayName:str
    connectedGateway:str
    subnet:dict
    revision:int