import json
import logging
import sys

from avs._avs_orchestrator import AVSOrchestrator
from avs.avsarconboarder.orchestrator.NSXOrchestrator._nsx_orchestrator import NSXOrchestor
from avs.avsarconboarder.orchestrator._orchestrator import Orchestrator
from avs.avsarconboarder.processor.nsx.helper._DNSHelper import DNSHelper
from avs.avsarconboarder.constants import Constant
from avs.avsarconboarder.utils.user_config_validatator import ConfigValidator
from avs.avsarconboarder.utils.utils import validate_region
from avs.converter._converter import Converter
from avs.converter.nsx.nsx_converter import DHCPConverter, SegmentConverter
from pkgs import ApplianceSetup, VMwareEnvSetup, ArcVMwareResources
from pkgs._exceptions import FilePathNotFoundInArgs, InvalidOperation, InternetNotEnabled, InvalidRegion
from avs.avsarconboarder.entity.request.arc_addon_request import ArcAddonRequest
from avs.avsarconboarder.creator.arcaddon.arc_addon_creator import ArcAddonCreator
from avs.avsarconboarder.deleter.arcadon.arc_addon_deleter import ArcAddonDeleter
from pkgs._utils import confirm_prompt

def register_with_private_cloud(customer_resource, vcenterId: str):
    arc_addon_creator = ArcAddonCreator()
    arc_addon_creator.create(customer_resource, ArcAddonRequest("Arc", vcenterId))


def deregister_from_private_cloud(customer_resource):
    arc_addon_deleter = ArcAddonDeleter()
    arc_addon_deleter.delete(customer_resource)


if __name__ == "__main__":
    try:
        operation = sys.argv[1]
    except IndexError:
        raise InvalidOperation(
            'Operation is not passed as argument. Supported versions are \"onboard\" and \"deboard\"')

    if operation not in ['onboard', 'deboard']:
        raise InvalidOperation('Supported versions are \"onboard\" and \"deboard\" ')

    file_path = None
    try:
        file_path = sys.argv[2]
    except IndexError:
        raise FilePathNotFoundInArgs('Config file path is not given in command line arguments.')
    config = None
    with open(file_path, 'r') as f:
        data = f.read()
        config = json.loads(data)

    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%dT%H:%M:%S')
    is_avs = False
    try:
        is_avs = config['isAVS']
    except KeyError:
        pass
    if is_avs:
        logging.info("avs enabled")
        avs_config_validator = ConfigValidator(config)
        avs_config_validator.validate_avs_config()
        avs_orchestrator: Orchestrator = AVSOrchestrator()
        _customer_details = avs_orchestrator.orchestrate(config)

        # TODO: Remove the Condition check after internal testing.
        #  This condition allows the user specified location to be use for creating RB, CL resources.
        #  If not sepecified the private cloud's location is used. This is the expected behavior.
        #  The former is enabled only to speed up internal testing
        if Constant.LOCATION not in config:
            config[Constant.LOCATION] = _customer_details.cloud_details[Constant.LOCATION]


        # TODO: Point to documentation link here for getting valid regions.
        if not validate_region(config[Constant.LOCATION]):
            raise InvalidRegion("This feature is not available in this region. Please refer to this document for valid regions.")

        # TODO: Remove the mandatory config called "register" after internal testing.
        #  This condition allows testing with and without the register API call.

    if operation == 'onboard':
        if is_avs:
            dhcp_data_converter: Converter = DHCPConverter()
            segment_data_converter: Converter = SegmentConverter()
            if config["isStatic"]:
                nsx_orchestrator: Orchestrator = NSXOrchestor(_customer_details,
                                                              dhcp_data_converter.convert_data(config),
                                                              segment_data_converter.convert_data(config))
            else:
                nsx_orchestrator: Orchestrator = NSXOrchestor(_customer_details,
                                                              None,
                                                              segment_data_converter.convert_data(config))
            nsx_orchestrator.orchestrate()
            # TODO Move the DNS Helper out of the processor
            if config["isStatic"]:
                dns_helper = DNSHelper()
                dns_data = dns_helper.retrieve_dns_config(_customer_details.customer_resource, _customer_details.cloud_details)
                config[Constant.DNS_SERVICE_IP] = [dns_data.server_details['properties']['dnsServiceIp']]
        arc_vmware_res = ArcVMwareResources(config)
        appliance_setup = ApplianceSetup(config, arc_vmware_res)

        env_setup = VMwareEnvSetup(config)
        env_setup.setup()

        vcenterId = appliance_setup.create()
        if is_avs and config["register"]:
            register_with_private_cloud(_customer_details.customer_resource, vcenterId)
    elif operation == 'deboard':
        if is_avs and config["register"]:
            deregister_from_private_cloud(_customer_details.customer_resource)
        arc_vmware_res = ArcVMwareResources(config)
        appliance_setup = ApplianceSetup(config, arc_vmware_res)
        appliance_setup.delete()
    else:
        raise InvalidOperation(f"Invalid operation entered - {operation}")
