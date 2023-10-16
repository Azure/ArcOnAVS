import os
from urllib.parse import urlparse
from ...entity._vsphere_resource import VSphereResourceData
from ...retriever._retriever import Retriever
import logging
from .....pkgs._govc_cli import govc_cli
from .....pkgs._exceptions import vCenterOperationFailed

class VSphereDetails(Retriever):
    instance = None
    _arc_rp_name = "arc-rp"
    _arc_folder_name = "arc-folder"
    _template_name = "arc-template"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance
    
    def retrieve_cluster_name(self):
        logging.info("retriece_cluster_name")
        res, err = govc_cli('find', '-type', 'c')
        print(type(res))
        print(res)
        if err:
            raise vCenterOperationFailed('Retrieving of clusters failed')
        logging.info("cluster info retrieved successfully")
        return res[0]
    
    def retrieve_datastore_name(self):
        logging.info("retriece_datastore_name")
        res, err = govc_cli('find', '-type', 's')
        print(type(res))
        print(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datastore failed')
        logging.info("datastore info retrieved successfully")
        dataStorePath = res[0].split("/")
        return dataStorePath[-1]
    
    def retrieve_datacenter_name(self):
        logging.info("in retrieve_data_center info")
        res, err = govc_cli('datacenter.info')
        print(type(res))
        print(res)
        if err:
            raise vCenterOperationFailed('Retrieving of datacenter failed')
        logging.info("datacenter info retrieved successfully")
        return res[0]["Name"]
    
    def _set_vcenter_cred(self, cloud_details, vcenter_credentials):
        url_data = urlparse(cloud_details['vcsa_endpoint'])
        vCenter_address= url_data.netloc + '443'
        os.environ['GOVC_INSECURE'] = "true"
        os.environ['GOVC_URL'] = f"https://{vCenter_address}/sdk"
        os.environ['GOVC_USERNAME'] = f"{vcenter_credentials.username}"
        os.environ['GOVC_PASSWORD'] = f"{vcenter_credentials.password}"

    def retrieve_data(self, *args):
        self._set_vcenter_cred(args[0], args[1])
        cluster_name_path = self.retrieve_cluster_name()
        _arc_rp = os.path.join(cluster_name_path, f"/Resources/{self._arc_rp_name}")
        _datacenter = self.retrieve_datacenter_name()
        _arc_folder = os.path.join(f"/{_datacenter}",f"/vm/{self._arc_folder_name}")
        _data_store = self.retrieve_datastore_name()
        return VSphereResourceData(resourcePool=_arc_rp,
                                   folder=_arc_folder, dataStore=_data_store,
                                   datacenter=_datacenter, vmTemplateName=self._template_name)
    