from ...entity._vsphere_resource import VSphereResourceData
from ...retriever._retriever import Retriever


class VSphereDetails(Retriever):
    instance = None
    _arc_rp = "arc-rp"
    _arc_folder = "arc-folder"
    _data_center = "SDDC-Datacenter"
    _data_store = "vsanDatastore"
    _template_name = "arc-template"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def retrieve_data(self, object):
        return VSphereResourceData(resourcePool=self._arc_rp,
                                   folder=self._arc_folder, dataStore=self._data_store,
                                   datacenter=self._data_center, vmTemplateName=self._template_name);