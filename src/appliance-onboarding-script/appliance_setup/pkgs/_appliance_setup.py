import json, yaml, requests
from pathlib import Path
import logging
from ._exceptions import AzCommandError, InvalidOperation, ProgramExit, ArmFeatureNotRegistered, \
    ClusterExtensionCreationFailed, ArmProviderNotRegistered
from ._az_cli import az_cli
from ._checks_and_validations import _wait_until_appliance_is_in_running_state
from ._utils import TempChangeDir, confirm_prompt, decode_base64, delete_empty_sub_dicts, delete_unassigned_fields, get_value_using_path_in_dict, set_value_using_path_in_dict, create_dir_if_doesnot_exist, get_vm_snapshot_name
from . import _templates as templates
from shutil import copy
from ._arcvmware_resources import ArcVMwareResources
import os


class ApplianceSetup(object):

    _key_map: dict = {
        'vmware-appliance': {
            'applianceControlPlaneIpAddress': 'applianceClusterConfig.controlPlaneEndpoint',
            'proxyDetails.http': 'applianceClusterConfig.networking.proxy.http',
            'proxyDetails.https': 'applianceClusterConfig.networking.proxy.https',
            'proxyDetails.noProxy': 'applianceClusterConfig.networking.proxy.noproxy',
            'proxyDetails.certificateFilePath': 'applianceClusterConfig.networking.proxy.certificateFilePath'
        },

        'vmware-resource': {
            'resourceGroup': 'resource.resource_group',
            'nameForApplianceInAzure': 'resource.name',
            'location': 'resource.location',
            'subscriptionId': 'resource.subscription'
        },

        'vmware-infra': {
            'vCenterAddress': 'vsphereprovider.credentials.address',
            'vCenterUserName': 'vsphereprovider.credentials.username',
            'vCenterPassword': 'vsphereprovider.credentials.password',
            'datacenterForApplianceVM': 'vsphereprovider.datacenter',
            'datastoreForApplianceVM': 'vsphereprovider.datastore',
            'resourcePoolForApplianceVM': 'vsphereprovider.resourcepool',
            'networkForApplianceVM': 'vsphereprovider.network.segment',
            'staticIpNetworkDetails.networkForApplianceVM': 'vsphereprovider.network.segment',
            'staticIpNetworkDetails.k8sNodeIPPoolStart': 'vsphereprovider.network.k8snodeippoolstart',
            'staticIpNetworkDetails.k8sNodeIPPoolEnd': 'vsphereprovider.network.k8snodeippoolend',
            'staticIpNetworkDetails.networkCIDRForApplianceVM': 'vsphereprovider.network.ipaddressprefix',
            'staticIpNetworkDetails.gatewayIPAddress': 'vsphereprovider.network.gateway',
            'DHCPNetworkDetails.networkForApplianceVM': 'vsphereprovider.network.segment',
            'folderForApplianceVM': 'vsphereprovider.folder',
            'DNS_Service_IP': 'vsphereprovider.network.dnsservers',

            'vmTemplateName': 'vsphereprovider.appliancevm.vmtemplate',
            'diskSizeGibForApplianceVM': 'vsphereprovider.disksizegib',
            'memoryMibForApplianceVM': 'vsphereprovider.memorymib',
            'numCpusForApplianceVM': 'vsphereprovider.numcpus'
        }
    }

    # Atleast one feature from provided listed under a namespace should be registered.
    _list_of_required_features = [
        {
            'feature': ['Appliances-ppauto', 'Appliances-pp'],
            'namespace': 'Microsoft.ResourceConnector'
        },
        {
            'feature': 'ConnectedVMwarePreview',
            'namespace': 'Microsoft.ConnectedVMwarevSphere'
        },
        {
            'namespace': 'Microsoft.KubernetesConfiguration'
        },
        {
            'namespace': 'Microsoft.ExtendedLocation'
        },
        {
            'feature': 'AzureArcForAVS',
            'namespace': 'Microsoft.AVS'
        }
    ]


    _config: dict
    _temp_dir: str = '.temp'

    _local_appliance_yaml: str
    _local_resource_yaml: str
    _local_infra_yaml: str

    _arc_vmware_resources: ArcVMwareResources
    _default_extension = 'Microsoft.VMware'
    _default_release_train = "stable"
    _vmware_rp_sp_id = "ac9dc5fe-b644-4832-9d03-d9f1ab70c5f7"

    def __init__(self, config: dict, arc_vmware_resources: ArcVMwareResources):
        self._config = config
        self._local_appliance_yaml: str = self._temp_dir + '/vmware-appliance.yaml'
        self._local_resource_yaml: str = self._temp_dir + '/vmware-resource.yaml'
        self._local_infra_yaml: str = self._temp_dir + '/vmware-infra.yaml'
        self._local_vmware_extension: str = self._temp_dir + '/vmware-extension.json'
        self._arc_vmware_resources = arc_vmware_resources

    def _copy_proxy_cert_update_config(self):
        config = self._config
        if 'proxyDetails' in config and 'certificateFilePath' in config['proxyDetails']:
            f: str = config['proxyDetails']['certificateFilePath']
            if not os.path.exists(f):
                raise FileExistsError(f'{f} does not exist.')
            copy(f, self._temp_dir)
            fp = Path(f)
            config['proxyDetails']['certificateFilePath'] = fp.name

    def create(self):
        self._create_template_files()
        self._update_local_yaml_with_user_config()
        self._set_default_subscription()
        self._check_if_provider_is_registered()
        self._check_if_required_features_registered()
        self._validate_appliance()
        self._prepare_appliance()
        appliance_id = self._deploy_and_create_appliance()
        extension_id = self._create_or_delete_vmware_extension('create')
        if extension_id is not None:
            return self._arc_vmware_resources.create(appliance_id, extension_id)

    def _check_if_provider_is_registered(self):
        for item in self._list_of_required_features:
            namespace: str = item['namespace']

            logging.info(f'Checking if provider {namespace} is registered')
            res, err = az_cli('provider', 'show', '--namespace', f'"{namespace}"')
            if err:
                raise AzCommandError('Checking provider registration failed')
            res = json.loads(res)
            registrationState = res["registrationState"]
            if registrationState != "Registered":
                raise ArmProviderNotRegistered(f'The provider namespace {namespace} should be registered')

    def _check_if_required_features_registered(self):
        for item in self._list_of_required_features:
            if 'feature' not in item:
                continue
            required_features_list = item['feature']
            namespace: str = item['namespace']
            if type(required_features_list) != list:
                required_features_list = [required_features_list,]
            required_features_list = [f'{namespace.lower()}/{x.lower()}' for x in required_features_list]
            res, err = az_cli('feature', 'list', '--namespace', f'"{namespace}"')
            if err:
                raise AzCommandError(f'Not able to get the features under namespace {namespace}')
            res = json.loads(res)
            registered_featues = list(filter(lambda x: x['properties']['state'] == 'Registered', res))
            registered_featues = list(map(lambda x: x['name'].lower(), registered_featues))
            if len(set(required_features_list).intersection(registered_featues)) <= 0:
                required_features_list = item['feature']
                raise ArmFeatureNotRegistered(f'Atleast one feature should be registered from list {required_features_list} under namespace {namespace}')

    def delete(self):
        if not confirm_prompt('Do you want to proceed with delete appliance operation?'):
            return
        self._create_template_files()
        self._update_local_yaml_with_user_config()
        self._set_default_subscription()
        try:
            self._arc_vmware_resources.delete()
        except AzCommandError as e:
            logging.info(e)
        try:
            self._create_or_delete_vmware_extension('delete')
        except AzCommandError as e:
            logging.info(e)
        self._delete_appliance()

    def _check_if_apiserver_is_reachable(self):
        config = self._config
        try:
            apiserver_address = config['applianceControlPlaneIpAddress']
            res = requests.get(f'https://{apiserver_address}:6443/livez', verify=False, timeout=10)
            return res.ok
        except requests.exceptions.ConnectionError:
            pass
        return False

    def _validate_appliance(self):
        with TempChangeDir(self._temp_dir):
            config = self._config

            logging.info('Validating appliance config...')
            err = os.system(' '.join(['az', 'arcappliance', 'validate', 'vmware', '--debug',
                '--config-file', 'vmware-appliance.yaml',]))

            # TODO: Uncomment the block below. Currently arc appliance validate command  returns error even for
            #  correct config. Once this is fixed, the following can be uncommented.

            # if err:
                # raise AzCommandError('arcappliance Validate command failed. Fix the configuration and try again. The error is {}'.format(err))

    def _prepare_appliance(self):
        with TempChangeDir(self._temp_dir):
            config = self._config

            logging.info('Preparing appliance...')
            err = os.system(' '.join(['az', 'arcappliance', 'prepare', 'vmware', '--debug',
                '--config-file', 'vmware-appliance.yaml',]))
            if err:
                raise AzCommandError('arcappliance prepare command failed.')

    def _deploy_and_create_appliance(self) -> str:
        is_api_server_reachable = self._check_if_apiserver_is_reachable()
        with TempChangeDir(self._temp_dir):
            config = self._config
            apiserver_address = config['applianceControlPlaneIpAddress']
            if is_api_server_reachable and not confirm_prompt(f'An ApiServer is already reachable on endpoint {apiserver_address}. Deployment will be skipped. Do you want to continue?'):
                raise ProgramExit('User chose to exit the program.')
            if not is_api_server_reachable:
                logging.info('Deploying appliance...')
                err = os.system(' '.join(['az', 'arcappliance', 'deploy', 'vmware', '--debug',
                    '--config-file', 'vmware-appliance.yaml',]))
                if err:
                    if not confirm_prompt('Deployment failed. Still want to proceed?'):
                        raise AzCommandError('arcappliance deploy command failed.')
                try:
                    copy('kubeconfig', '../')
                except:
                    pass
            else:
                logging.info('Skipping deploy step...')

            logging.info('Create appliance ARM resource...')
            res, err = az_cli('arcappliance', 'create', 'vmware', '--debug',
                '--config-file', 'vmware-appliance.yaml',
                '--kubeconfig', 'kubeconfig')
            if err:
                raise AzCommandError('arcappliance create command failed.')
            res = json.loads(res)
            logging.info("Successfully provisioned arcappliance arm resource.")
            return res['id']

    def _set_default_subscription(self):
        config = self._config
        sub = config['subscriptionId']
        _, err = az_cli('account', 'set', '-s', f'"{sub}"')
        if err:
            raise AzCommandError('Default subscription set command failed.')


    def _delete_appliance(self):
        with TempChangeDir(self._temp_dir):
            logging.info('Deleting appliance...')
            err = os.system(' '.join(['az', 'arcappliance', 'delete', 'vmware', '-y',
                '--config-file', 'vmware-appliance.yaml',
                '--debug']))
            if err:
                raise AzCommandError('arcappliance delete command failed.')

    def _create_or_delete_vmware_extension(self, op='create') -> str:
        config = self._config
        if op not in ['create', 'delete']:
            raise InvalidOperation('Supported operations are \"create\" and \"delete\".')
        name = 'azure-vmwareoperator'
        rg = config['resourceGroup']
        appliance_name = config['nameForApplianceInAzure']

        release_train = self._default_release_train
        if 'vmwareExtensionReleaseTrain' in config:
            release_train = config['vmwareExtensionReleaseTrain']

        extension_type = self._default_extension
        try:
            if config['isAVS']:
                extension_type = 'Microsoft.AVS'
        except KeyError:
            pass

        vmware_rp_sp, err = az_cli('ad', 'sp', 'show', '--id', f'"{self._vmware_rp_sp_id}"')
        if err:
            raise AzCommandError("Unable to get VMware SP object id.")

        vmware_rp_sp = json.loads(vmware_rp_sp)
        vmware_rp_object_id = vmware_rp_sp["objectId"]

        res = None
        if op == 'create':

            _wait_until_appliance_is_in_running_state(config, "Create K8s Extension")

            logging.info('Creating VMware extension...')
            res, err = az_cli('k8s-extension', 'create', '--debug',
                '-n', name,
                '-g', rg,
                '--cluster-name', f'"{appliance_name}"',
                '--cluster-type', 'appliances',
                '--scope', 'cluster',
                '--extension-type', f'"{extension_type}"',
                '--release-train', f'"{release_train}"',
                '--release-namespace', f'"{name}"',
                '--auto-upgrade', 'true',
                '--config', 'Microsoft.CustomLocation.ServiceAccount=azure-vmwareoperator'
                '--config', f'global.rpObjectId="{vmware_rp_object_id}"'
            )
            if err:
                raise AzCommandError(f'Create k8s-extension instance failed.')
            res = json.loads(res)
            if res['provisioningState'] != 'Succeeded':
                raise ClusterExtensionCreationFailed(f"cluster extension creation failed. response id {res}")
            return res['id']
        else:
            logging.info('Deleting VMware extension...')
            _, err = az_cli('k8s-extension', 'delete', '--debug', '-y',
                '-n', 'azure-vmwareoperator',
                '-g', f'"{rg}"',
                '--cluster-name', f'"{appliance_name}"',
                '--cluster-type', 'appliances',
            )
            if err:
                raise AzCommandError(f'Delete k8s-extension instance failed.')

    def _create_template_files(self):
        create_dir_if_doesnot_exist(self._temp_dir)
        with TempChangeDir(self._temp_dir):
            with open('vmware-appliance.yaml', 'w') as f:
                data = templates.vmware_appliance
                f.write(decode_base64(data))

        with TempChangeDir(self._temp_dir):
            with open('vmware-resource.yaml', 'w') as f:
                data = templates.vmware_resource
                f.write(decode_base64(data))

        with TempChangeDir(self._temp_dir):
            with open('vmware-infra.yaml', 'w') as f:
                data = templates.vmware_infra
                f.write(decode_base64(data))

    def _delete_keys_if_empty(self):
        config = self._config
        try:
            v = config['proxyDetails']['certificateFilePath']
            if str.strip(v) == "":
                del config['proxyDetails']['certificateFilePath']
        except KeyError:
            pass

    def _update_local_yaml_with_user_config(self):
        self._delete_keys_if_empty()
        self._copy_proxy_cert_update_config()
        config = self._config
        config['vCenterAddress'] = config['vCenterFQDN'] + ':' + config['vCenterPort']
        appliance: dict = None
        infra: dict = None
        resource: dict = None
        with open(self._local_appliance_yaml, 'r') as f:
            t = f.read()
            appliance = yaml.safe_load(t)
        with open(self._local_resource_yaml, 'r') as f:
            t = f.read()
            resource = yaml.safe_load(t)
        with open(self._local_infra_yaml, 'r') as f:
            t = f.read()
            location = config['location']
            location = ''.join(location.split(' ')).lower()
            t = t.format(location=location)
            infra = yaml.safe_load(t)

        for k, v in self._key_map['vmware-appliance'].items():
            try:
                value = get_value_using_path_in_dict(config, k)
            except KeyError:
                continue
            set_value_using_path_in_dict(appliance, v, value)

        for k, v in self._key_map['vmware-resource'].items():
            try:
                value = get_value_using_path_in_dict(config, k)
            except KeyError:
                continue
            set_value_using_path_in_dict(resource, v, value)

        for k, v in self._key_map['vmware-infra'].items():
            try:
                value = get_value_using_path_in_dict(config, k)
            except KeyError:
                continue
            set_value_using_path_in_dict(infra, v, value)

        appliance = delete_unassigned_fields(appliance)
        resource = delete_unassigned_fields(resource)
        infra = delete_unassigned_fields(infra)
        delete_empty_sub_dicts(appliance)
        delete_empty_sub_dicts(resource)
        delete_empty_sub_dicts(infra)

        with open(self._local_appliance_yaml, 'w') as f:
            t = yaml.safe_dump(appliance)
            f.write(t)
        with open(self._local_resource_yaml, 'w') as f:
            t = yaml.safe_dump(resource)
            f.write(t)
        with open(self._local_infra_yaml, 'w') as f:
            t = yaml.safe_dump(infra)
            f.write(t)

