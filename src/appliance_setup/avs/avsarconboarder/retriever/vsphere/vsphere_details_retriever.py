import os
import json
from urllib.parse import urlparse
from ...entity._vsphere_resource import VSphereResourceData
from ...retriever._retriever import Retriever
import logging
from pkgs._govc_cli import govc_cli
from pkgs._exceptions import vCenterOperationFailed

class VSphereDetails(Retriever):
    instance = None
    _arc_rp_name = "arc-rp"
    _arc_folder_name = "arc-folder"
    _template_name = "arc-template"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    
    def _retrieve_cluster_name(self, data_center):
        res, err = govc_cli('find', '-type', 'c', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of clusters failed')
        logging.info("cluster info retrieved successfully")
        for cluster in res:
            if cluster.startswith(f'/{data_center}/'):
                return cluster
            
        raise vCenterOperationFailed(f'No cluster available in Datacenter {data_center}')
    
    def _retrieve_datastore_name(self, data_center):
        res, err = govc_cli('find', '-type', 's', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datastore failed')
        logging.info("datastore info retrieved successfully")

        for data_store in res:
            if data_store.startswith(f'/{data_center}/'):
                data_store_path = res[0].split("/")
                return data_store_path[-1]
            
        raise vCenterOperationFailed(f'No datastore available in Datacenter {data_center}')
    
    def _set_vcenter_cred(self, cloud_details, vcenter_credentials):
        url_data = urlparse(cloud_details['vcsa_endpoint'])
        vCenter_address= url_data.netloc + ':443'
        os.environ['GOVC_INSECURE'] = "true"
        os.environ['GOVC_URL'] = f"https://{vCenter_address}/sdk"
        os.environ['GOVC_USERNAME'] = f"{vcenter_credentials.username}"
        os.environ['GOVC_PASSWORD'] = f"{vcenter_credentials.password}"

    def _retrieve_environment_details(self):
        res, err = govc_cli('datacenter.info', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datacenter info failed')
        logging.info("datacenter info retrieved successfully")

        for data_center in res["Datacenters"]:
            data_center_name = data_center["Name"]
            try:
                data_store = self._retrieve_datastore_name(data_center_name)
                cluster = self._retrieve_cluster_name(data_center_name)
                return data_center_name,data_store,cluster
            except:
                continue

        raise vCenterOperationFailed('No DataStore and cluster found to be provisioned for Arc Applaince')

    def retrieve_data(self, *args):
        self._set_vcenter_cred(args[0], args[1])
        data_center, data_store, cluster_name_path, = self._retrieve_environment_details()
        arc_rp = f"{cluster_name_path}/Resources/{self._arc_rp_name}"
        arc_folder = f"/{data_center}/vm/{self._arc_folder_name}"
        return VSphereResourceData(resourcePool=arc_rp,
                                   folder=arc_folder, dataStore=data_store,
                                   datacenter=data_center, vmTemplateName=self._template_name)
    