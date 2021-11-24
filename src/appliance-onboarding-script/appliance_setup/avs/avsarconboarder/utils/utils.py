from avs.avsarconboarder.constants import Constant


def validate_region(region: str):
    valid_regions = Constant.VALID_LOCATIONS.split(",")
    if region in valid_regions:
        return True
    return False
