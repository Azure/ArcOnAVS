import json
import logging
import re

from pkgs._utils import safe_quote_string
from ._az_cli import az_cli
from ._exceptions import AzCommandError
from ._azure_resource_validations import _wait_until_appliance_is_in_running_state

class ArcVMwareResources(object):

    _config: dict

    def __init__(self, config: dict) -> None:
        self._config = config

    def create(self, appliance_id, extension_id):
        cl = self._create_cl(appliance_id, extension_id)
        if cl is not None:
            return self._connect_vcenter(cl)

    def delete(self):
        try:
            self._delete_vcenter()
        except AzCommandError as e:
            logging.error(e)
        self._delete_cl()

    def _create_cl(self, appliance_id, extension_id) -> str:
        config = self._config

        logging.info('Creating Custom Location...')

        _wait_until_appliance_is_in_running_state(config)

        location = config['location']
        rg = config['resourceGroup']
        name = config['customLocationAzureName']
        k8s_namespace = re.sub('[^a-zA-Z0-9-]', '-', name.lower())
        res, err = az_cli('customlocation', 'create',
            '--resource-group', f'"{rg}"',
            '--name', f'"{name}"',
            '--cluster-extension-ids', f'"{extension_id}"',
            '--host-resource-id', f'"{appliance_id}"',
            '--namespace', f'"{k8s_namespace}"',
            '--location', f'"{location}"'
        )
        if err:
            raise AzCommandError('Create Custom Location failed.')
        res = json.loads(res)
        return res['id']

    def _delete_cl(self):
        config = self._config
        logging.info('Deleting Custom Location...')
        rg = config['resourceGroup']
        name = config['customLocationAzureName']
        _, err = az_cli('customlocation', 'delete', '-y',
            '--resource-group', f'"{rg}"',
            '--name', f'"{name}"'
        )
        if err:
            raise AzCommandError('Delete Custom Location failed.')

    def _connect_vcenter(self, custom_location_id: str):
        config = self._config

        logging.info('Connecting vCenter...')

        _wait_until_appliance_is_in_running_state(config)
        
        location = config['location']
        rg = config['resourceGroup']
        name = config['nameForVCenterInAzure']
        fqdn = config['vCenterFQDN']
        port = config['vCenterPort']
        username = config['vCenterUserName']
        password = config['vCenterPassword']
        res, err = az_cli('connectedvmware', 'vcenter', 'connect',
            '--resource-group', f'"{rg}"',
            '--name', f'"{name}"',
            '--location', f'"{location}"',
            '--custom-location', f'"{custom_location_id}"',
            '--fqdn', f'"{fqdn}"',
            '--port', f'"{port}"',
            '--username', f'"{username}"',
            '--password', safe_quote_string(password)
        )
        res = json.loads(res)
        if err:
            raise AzCommandError('Connect vCenter failed.')
        return res['id']

    def _delete_vcenter(self):
        config = self._config
        logging.info('Deleting vCenter...')
        rg = config['resourceGroup']
        name = config['nameForVCenterInAzure']
        _, err = az_cli('connectedvmware', 'vcenter', 'delete', '--yes',
            '--resource-group', f'"{rg}"',
            '--name', f'"{name}"',
        )
        if err:
            raise AzCommandError('Delete vCenter failed.')
        
