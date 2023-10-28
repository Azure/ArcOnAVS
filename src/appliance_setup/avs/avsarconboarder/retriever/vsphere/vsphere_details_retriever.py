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
    
    def _retrieve_clusters(self):
        res, err = govc_cli('find', '-type', 'c', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of clusters failed')
        logging.info("cluster info retrieved successfully")
        return res
    
    def _retrieve_data_stores(self):
        res, err = govc_cli('find', '-type', 's', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datastore failed')
        logging.info("datastore info retrieved successfully")
        return res
    
    def _set_vcenter_cred(self, cloud_details, vcenter_credentials):
        url_data = urlparse(cloud_details['vcsa_endpoint'])
        vCenter_address= url_data.netloc + ':443'
        os.environ['GOVC_INSECURE'] = "true"
        os.environ['GOVC_URL'] = f"https://{vCenter_address}/sdk"
        os.environ['GOVC_USERNAME'] = f"{vcenter_credentials.username}"
        os.environ['GOVC_PASSWORD'] = f"{vcenter_credentials.password}"

    def _retrieve_data_centers(self):
        res, err = govc_cli('datacenter.info', ' -json=true')
        res = json.loads(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datacenter info failed')
        logging.info("datacenter info retrieved successfully")
        return res["Datacenters"]
    
    def _retrieve_default_values_if_present(self, data_centers, data_stores, clusters):
        for data_center in data_centers:
            data_center_name = None 
            cluster_name = None
            data_store_name = None
            if(data_center["Name"] == "SDDC-Datacenter"):
                data_center_name = data_center["Name"]
                for data_store in data_stores:
                    if data_store.startswith(f'/{data_center_name}/'):
                        data_store_path = data_store.split("/")
                        if(data_store_path[-1] == "vsanDataStore"):
                            data_store_name = data_store_path[-1]
                            break
                for cluster in clusters:
                    if cluster.startswith(f'/{data_center_name}/'):
                        cluster_path = cluster.split("/")
                        if(cluster_path[-1] == "Cluster-1"):
                            cluster_name = cluster
                            break
                
        return data_center_name, data_store_name, cluster_name

    def _retrieve_environment_details(self):
        data_centers = self._retrieve_data_centers()
        data_stores = self._retrieve_data_stores()
        clusters = self._retrieve_clusters()

        default_data_center, default_data_store, default_cluster = self._retrieve_default_values_if_present(data_centers, data_stores, clusters)

        if default_data_center != None and default_data_store != None and default_cluster != None:
            logging.info("Default Datacenter, DataStore, Cluster available")
            return default_data_center, default_data_store, default_cluster

        for data_center in data_centers:
            data_center_name = data_center["Name"]
            cluster_name = None
            data_store_name = None
            for data_store in data_stores:
                if data_store.startswith(f'/{data_center_name}/'):
                    data_store_path = data_store.split("/")
                    data_store_name = data_store_path[-1]
                    break
            for cluster in clusters:
                if cluster.startswith(f'/{data_center_name}/'):
                    cluster_name = cluster
                    break
            
            if data_center_name!= None and cluster_name != None and data_store_name != None:
                return data_center_name, data_store_name, cluster_name

        raise vCenterOperationFailed('No DataCenter, DataStore and cluster found to be provisioned for Arc Applaince')

    def retrieve_data(self, *args):
        self._set_vcenter_cred(args[0], args[1])
        data_center, data_store, cluster_name_path, = self._retrieve_environment_details()
        arc_rp = f"{cluster_name_path}/Resources/{self._arc_rp_name}"
        arc_folder = f"/{data_center}/vm/{self._arc_folder_name}"
        return VSphereResourceData(resourcePool=arc_rp,
                                   folder=arc_folder, dataStore=data_store,
                                   datacenter=data_center, vmTemplateName=self._template_name)
    