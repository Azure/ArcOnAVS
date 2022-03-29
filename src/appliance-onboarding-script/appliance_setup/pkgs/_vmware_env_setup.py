import logging
from ._exceptions import InvalidInputError, vCenterOperationFailed
from ._govc_cli import govc_cli
import os, json
from ._utils import get_vm_snapshot_name, confirm_prompt


class VMwareEnvSetup(object):

    _temp_dir: str = '.temp'
    _template_opt_file_name: str = 'template-options.json'
    _file_path: str

    def __init__(self, config: dict) -> None:
        self._config = config

    def setup(self):
        self._set_vcenter_cred()
        try:
            if self._config['isAVS']:
                self._create_folder()
                self._create_resource_pool()
        except KeyError:
            pass

    def _set_vcenter_cred(self):
        config = self._config
        address = config['vCenterFQDN'] + ':' + config['vCenterPort']
        username = config['vCenterUserName']
        password = config['vCenterPassword']
        os.environ['GOVC_INSECURE'] = "true"
        os.environ['GOVC_URL'] = f"https://{address}/sdk"
        os.environ['GOVC_USERNAME'] = f"{username}"
        os.environ['GOVC_PASSWORD'] = f"{password}"

    def _create_folder(self):
        logging.info("in _create_folder")
        folder = self._config['folderForApplianceVM']
        datacenter = self._config['datacenterForApplianceVM']
        if self._folder_exists(folder):
            logging.info("folder already exists")
            return
        _, err = govc_cli('folder.create', folder)
        if err:
            raise vCenterOperationFailed('Folder creation failed.')
        logging.info("folder created successfully")
        return

    def _folder_exists(self, folder_name: str):
        _, err = govc_cli('folder.info', folder_name)
        if err:
            return False
        return True

    def _create_resource_pool(self):
        logging.info("in _create_resource_pool")
        resource_pool = self._config['resourcePoolForApplianceVM']
        datacenter = self._config['datacenterForApplianceVM']
        if self._resource_pool_exists(resource_pool):
            logging.info("resource pool already exists")
            return
        _, err = govc_cli('pool.create', resource_pool)
        if err:
            raise vCenterOperationFailed('Resource Pool creation failed.')
        logging.info("resource pool created successfully")
        return

    def _resource_pool_exists(self, res_pool_name):
        logging.info("in method _resource_pool_exists for pool name :: " + res_pool_name)
        res_pool_info, err = govc_cli('pool.info', res_pool_name)
        logging.info("res_pool_info :: " + res_pool_info)
        if res_pool_info == "" or err:
            return False
        return True