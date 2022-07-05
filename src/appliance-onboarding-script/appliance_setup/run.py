import json
import logging
import os
import sys
from datetime import datetime
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
from pkgs._exceptions import FilePathNotFoundInArgs, InvalidOperation, InternetNotEnabled, InvalidRegion, ProgramExit
from avs.avsarconboarder.entity.request.arc_addon_request import ArcAddonRequest
from avs.avsarconboarder.creator.arcaddon.arc_addon_creator import ArcAddonCreator
from avs.avsarconboarder.deleter.arcadon.arc_addon_deleter import ArcAddonDeleter
from pkgs._utils import confirm_prompt

def logger_setup(logLevel = logging.INFO):
    log_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    LOG_DIR = "logs"
    current_time = datetime.now().strftime('%Y-%m-%d-%H.%M.%S') # To avoid ":" in file names.
    LOG_FILE_ERROR = f'log_{current_time}.err'
    LOG_FILE_INFO = f'log_{current_time}.info'
    LOG_FILE_DEBUG = f'log_{current_time}.debug'

    # Create logs directory if it does not already exist
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    # get the root logger
    log = logging.getLogger()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    # Critical, Error and Warning go to this file
    if logLevel <= logging.WARNING:
        file_handler_warning = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_ERROR), mode='a')
        file_handler_warning.setFormatter(log_formatter)
        file_handler_warning.setLevel(logging.WARNING)
        log.addHandler(file_handler_warning)

    # Info goes to this file
    if logLevel <= logging.INFO:
        file_handler_info = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_INFO), mode='a')
        file_handler_info.setFormatter(log_formatter)
        file_handler_info.setLevel(logging.INFO)
        log.addHandler(file_handler_info)

    # Debug goes to this file
    if logLevel <= logging.DEBUG:
        file_handler_debug = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_DEBUG), mode='a')
        file_handler_debug.setFormatter(log_formatter)
        file_handler_debug.setLevel(logging.DEBUG)
        log.addHandler(file_handler_debug)

    log.setLevel(logLevel)


def register_with_private_cloud(customer_resource, vcenterId: str):
    arc_addon_creator = ArcAddonCreator()
    arc_addon_creator.create(customer_resource, ArcAddonRequest("Arc", vcenterId))


def deregister_from_private_cloud(customer_resource):
    arc_addon_deleter = ArcAddonDeleter()
    arc_addon_deleter.delete(customer_resource)

def _populate_default_values_of_optional_fields_in_config(config):
    config["isAVS"] = config.get("isAVS", True)
    config["register"] = config.get("register", True)

    #TODO: Remove isStatic default when we support DHCP Configuration
    config["isStatic"] = config.get("isStatic", True)

if __name__ == "__main__":
    try:
        operation = sys.argv[1]
    except IndexError:
        raise InvalidOperation(
            'Operation is not passed as argument. Supported versions are \"onboard\" and \"offboard\"')

    if operation not in ['onboard', 'offboard']:
        raise InvalidOperation('Supported versions are \"onboard\" and \"offboard\" ')

    file_path = None
    try:
        file_path = sys.argv[2]
    except IndexError:
        raise FilePathNotFoundInArgs('Config file path is not given in command line arguments.')
    config = None
    with open(file_path, 'r') as f:
        data = f.read()
        config = json.loads(data)

    try:
        log_level = sys.argv[3]
    except IndexError:
        log_level = "INFO"

    try:
        isAutomated = (sys.argv[4].lower() == 'true') # isAutomated Parameter is set to true if it is an automation testing Run. 
                                                      # In case this param is true, we use az login --identity, which logs in Azure VM's identity
                                                      # and skip the confirm prompts.
    except IndexError:
        isAutomated = False;
    
    log_level_dict = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    if log_level not in log_level_dict.keys():
        raise InvalidOperation('Entered log level {} is not supported. Supported loglevels are {}'.format(log_level, log_level_dict.keys()))

    logger_setup(log_level_dict[log_level])

    _populate_default_values_of_optional_fields_in_config(config)

    if config["isAVS"]:
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
            raise InvalidRegion(f"This feature is only available in these regions: {Constant.VALID_LOCATIONS}")

    if operation == 'onboard':
        if config["isAVS"]:
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
        appliance_setup = ApplianceSetup(config, arc_vmware_res, isAutomated)

        env_setup = VMwareEnvSetup(config)
        env_setup.setup()

        vcenterId = appliance_setup.create()
        if config["isAVS"] and config["register"]:
            register_with_private_cloud(_customer_details.customer_resource, vcenterId)
    elif operation == 'offboard':
        # Removing confirm_prompts for automated testing
        if (isAutomated == False) and not confirm_prompt('Do you want to proceed with offboard operation?'):
            raise ProgramExit('User chose to exit the program.')
        if config["isAVS"] and config["register"]:
            deregister_from_private_cloud(_customer_details.customer_resource)
        arc_vmware_res = ArcVMwareResources(config)
        appliance_setup = ApplianceSetup(config, arc_vmware_res, isAutomated)
        appliance_setup.delete()
    else:
        raise InvalidOperation(f"Invalid operation entered - {operation}")
