from avs.avsarconboarder.constants import Constant


def validate_region(region: str):
    valid_regions = Constant.VALID_LOCATIONS.split(",")
    if region in valid_regions:
        return True
    return False

def bytes_to_string(b: bytes) -> str:
    return b.decode('UTF-8', errors='strict')