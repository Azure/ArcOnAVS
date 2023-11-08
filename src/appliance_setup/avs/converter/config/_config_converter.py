import logging
import re
from urllib.parse import urlparse

from ...avsarconboarder.entity.data.retrieved_data import CustomerDetails
from .._converter import Converter
from ...avsarconboarder.exception import InvalidInputError


class ConfigConverter(Converter):

    def convert_data(self, *args):
        customer_details: CustomerDetails = args[0]
        config = args[1]

        if customer_details is None or config is None and len(config) == 0:
            raise InvalidInputError("invalid input of config and customer details")

        try:
            self._update_config(config, customer_details)
            pass
        except KeyError as ke:
            logging.error("key error found :: ", ke)
            raise ke

    def _update_config(self, config, customer_details):
        self._update_appliance_name(config)
        self._update_credential_locations(config, customer_details)
        self._update_vcenter_inventory(config, customer_details)
        self._update_vcenter_customloc(config)
        self._update_appliance_vm_config(config)

    def _update_credential_locations(self, config, customer_details):
        url_data = urlparse(customer_details.cloud_details['vcsa_endpoint'])
        config['vCenterFQDN'] = url_data.netloc
        config['vCenterPort'] = '443'
        config['vCenterUserName'] = customer_details.vcenter_credentials.username
        config['vCenterPassword'] = customer_details.vcenter_credentials.password

    def _update_vcenter_inventory(self, config, customer_details):
        if customer_details.vsphere_resource_details is None:
            raise InvalidInputError('vsphere resource details absent from customer details')
        
        if ('datacenterForApplianceVM' not in config) or ('datacenterForApplianceVM' in config and config['datacenterForApplianceVM'] == ''):
            config['datacenterForApplianceVM'] = customer_details.vsphere_resource_details.datacenter

        if ('datastoreForApplianceVM' not in config) or ('datastoreForApplianceVM' in config and config['datastoreForApplianceVM'] == ''):    
            config['datastoreForApplianceVM'] = customer_details.vsphere_resource_details.dataStore

        if ('resourcePoolForApplianceVM' not in config) or ('resourcePoolForApplianceVM' in config and config['resourcePoolForApplianceVM'] == ''):
            config['resourcePoolForApplianceVM'] = customer_details.vsphere_resource_details.resourcePool

        if ('folderForApplianceVM' not in config) or ('folderForApplianceVM' in config and config['folderForApplianceVM'] == ''):
            config['folderForApplianceVM'] = customer_details.vsphere_resource_details.folder

        if ('vmTemplateName' not in config) or ('vmTemplateName' in config and config['vmTemplateName'] == ''):
            config['vmTemplateName'] = customer_details.vsphere_resource_details.vmTemplateName

    def _update_vcenter_customloc(self, config):
        pvc_name = self._sanitize_string(config['privateCloud'])
        if ('customLocationAzureName' not in config) or ('customLocationAzureName' in config and config['customLocationAzureName'] == ''):
            config['customLocationAzureName'] = pvc_name + '-custom-location'
        if ('nameForVCenterInAzure' not in config) or ('nameForVCenterInAzure' in config and config['nameForVCenterInAzure'] == ''):
            config['nameForVCenterInAzure'] = pvc_name + '-vcenter'

    def _update_appliance_name(self, config):
        pvc_name = self._sanitize_string(config['privateCloud'])
        if ('nameForApplianceInAzure' not in config) or ('nameForApplianceInAzure' in config and config['nameForApplianceInAzure'] == ''):
            config['nameForApplianceInAzure'] = pvc_name + '-resource-bridge'
        
    def _sanitize_string(self, value):
        if isinstance(value, str):
            return re.sub('[^a-zA-Z0-9-]', '-', value.lower())
        return value

    def _update_appliance_vm_config(self, config):
        config['diskSizeGibForApplianceVM'] = 100
        config['memoryMibForApplianceVM'] = 16384
        config['numCpusForApplianceVM'] = 4
