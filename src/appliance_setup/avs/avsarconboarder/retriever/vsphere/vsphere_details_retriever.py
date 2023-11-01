import os
import json
from urllib.parse import urlparse
import logging
from ...entity._vsphere_resource import VSphereResourceData
from ...retriever._retriever import Retriever
from pkgs._govc_cli import govc_cli, govc_build_sub_command
from pkgs._exceptions import vCenterOperationFailed

class VSphereDetails(Retriever):
    instance = None
    _data_center = "SDDC-Datacenter"
    _arc_rp_name = "arc-rp"
    _arc_folder_name = "arc-folder"
    _template_name = "arc-template"
    _arc_folder = f"/{_data_center}/vm/{_arc_folder_name}"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    
    def _find_cluster(self, data_store_name):    
        data_store_managed_cmd = self._managed_object_data_store_cmd(data_store_name)
        res, err = govc_cli('find', '.', '-type', 'c', '-datastore', data_store_managed_cmd)
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of associated cluster failed')
        logging.info("Retrieved associated cluster successfully")
        return res
    
    def _retrieve_data_stores(self):
        res, err = govc_cli('find', '-type', 's', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datastore failed')
        logging.info("datastore info retrieved successfully")
        return res
    
    def _managed_object_data_store_cmd(self, data_store_name):
        cmd = govc_build_sub_command('find', '-i', 'datastore', '-name', data_store_name)
        return cmd
    
    def _set_vcenter_cred(self, cloud_details, vcenter_credentials):
        url_data = urlparse(cloud_details['vcsa_endpoint'])
        vCenter_address= url_data.netloc + ':443'
        os.environ['GOVC_INSECURE'] = "true"
        os.environ['GOVC_URL'] = f"https://{vCenter_address}/sdk"
        os.environ['GOVC_USERNAME'] = f"{vcenter_credentials.username}"
        os.environ['GOVC_PASSWORD'] = f"{vcenter_credentials.password}"
    
    def _retrieve_default_values_if_present(self, data_stores):   
        cluster_path = None
        data_store_name = None   
        for data_store in data_stores:
            data_store_path_seperated = data_store.split("/")
            if(data_store_path_seperated[-1] == "vsanDatastore"):
                data_store_name = data_store_path_seperated[-1]
                cluster = self._find_cluster(data_store_name)
                cluster_path_seperated = cluster.split("/")
                if(cluster_path_seperated[-1] == "Cluster-1"):
                    cluster_path = cluster

        return data_store_name, cluster_path

    def _retrieve_environment_details(self):
        data_stores = self._retrieve_data_stores()

        try:
            default_data_store, default_cluster_path = self._retrieve_default_values_if_present(data_stores)
            if default_data_store != None and default_cluster_path != None:
                logging.info("Default DataStore, Cluster available")
                return default_data_store, default_cluster_path
        except:
            logging.info("Default DataStore, Cluster Not Available")

        cluster_path = None
        data_store_name = None   
        for data_store in data_stores:
            try:
                data_store_path_seperated = data_store.split("/")
                data_store_name = data_store_path_seperated[-1]
                cluster_path = self._find_cluster(data_store_name)
                
                if cluster_path != None and data_store_name != None:
                    return data_store_name, cluster_path
            except:
                continue

        raise vCenterOperationFailed('No DataStore and cluster found to be provisioned for Arc Applaince')

    def retrieve_data(self, *args):
        self._set_vcenter_cred(args[0], args[1])
        data_store, cluster_name_path = self._retrieve_environment_details()
        arc_rp = f"{cluster_name_path}/Resources/{self._arc_rp_name}"
        return VSphereResourceData(resourcePool=arc_rp,
                                   folder=self._arc_folder, dataStore=data_store,
                                   datacenter=self._data_center, vmTemplateName=self._template_name)
    