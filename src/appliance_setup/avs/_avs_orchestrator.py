import logging
import os
from json import JSONDecodeError

from .avsarconboarder.collector._DataCollector import DataCollector
from .avsarconboarder.entity.AzCli import AzCli
from .avsarconboarder.entity.CustomerResource import CustomerResource
from .avsarconboarder.entity._dhcpData import DHCPData
from .avsarconboarder.entity._segmentData import SegmentData
from .avsarconboarder.entity.data.retrieved_data import CustomerDetails
from .avsarconboarder.executor.azcli._AzCliExecutor import AzCliExecutor
from .avsarconboarder.orchestrator._orchestrator import Orchestrator
from .converter._converter import Converter
from .converter.config._config_converter import ConfigConverter


class AVSOrchestrator(Orchestrator):

    def __init__(self):
        self.data_collector = DataCollector()
        self.converter: Converter = ConfigConverter()
        self._az_cli_executor = AzCliExecutor() 
        pass

    def orchestrate(self, *args):
        config = args[0]
        logging.debug("config details :: ", config)
        self._set_default_subscription(config['subscriptionId'])
        appliance_name = None
        if 'nameForApplianceInAzure' in config:
            appliance_name = config['nameForApplianceInAzure']
        customer_res: CustomerResource = CustomerResource(config['resourceGroup'], config['subscriptionId'],
                                                          config['privateCloud'], appliance_name)
        customer_details: CustomerDetails = self.data_collector.collect_data(customer_res)
        self.converter.convert_data(customer_details, config)
        return customer_details

    def _set_default_subscription(self, sub_id):
        az_cli = AzCli().append('account').append('set').append("-s").append(sub_id)
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
        except JSONDecodeError as jde:
            logging.info("response for _set_default_subscription :: success")