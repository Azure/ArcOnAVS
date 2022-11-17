from ...entity._vsphere_resource import VSphereResourceData
from ...retriever._retriever import Retriever


class VSphereDetails(Retriever):
    instance = None
    _arc_rp_name = "arc-rp"
    _arc_folder_name = "arc-folder"
    _data_center = "SDDC-Datacenter"
    _data_store = "vsanDatastore"
    _template_name = "arc-template"
    _cluster_name = "Cluster-1"
    _arc_rp = f"/{_data_center}/host/{_cluster_name}/Resources/{_arc_rp_name}"
    _arc_folder = f"/{_data_center}/vm/{_arc_folder_name}"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def retrieve_data(self, object):
        return VSphereResourceData(resourcePool=self._arc_rp,
                                   folder=self._arc_folder, dataStore=self._data_store,
                                   datacenter=self._data_center, vmTemplateName=self._template_name);