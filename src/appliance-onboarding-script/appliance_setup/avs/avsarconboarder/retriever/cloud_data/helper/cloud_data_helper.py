from ....constants import Constant
from ....exception import VCSADetailsNotFoundException, InternetEnabledFlagNotFound, \
    ManagementClusterNotFound, VNETIPCIDRNotFound


class CloudDataHelper:
    
    _PROPERTIES = 'properties'
    _LOCATION = 'location'
    
    def __init__(self, cloud_details):
        self.cloud_details = cloud_details
        pass

    def get_vcsa_endpoint(self):
        print("finding vcsa endpoint")
        if self.cloud_details[self._PROPERTIES] is None and self.cloud_details[self._PROPERTIES]['endpoints'] is None and \
                self.cloud_details[self._PROPERTIES]['endpoints']['vcsa'] is None:
            raise VCSADetailsNotFoundException("vcsa details not found")
        return self.cloud_details[self._PROPERTIES]['endpoints']['vcsa']

    def find_internet_enabled(self):
        print("finding internet enabled")
        if self.cloud_details[self._PROPERTIES] is None and self.cloud_details[self._PROPERTIES][Constant.INTERNET] is None:
            raise InternetEnabledFlagNotFound("internet enabled details not found")
        if self.cloud_details[self._PROPERTIES][Constant.INTERNET] == 'Disabled':
            return False
        else:
            return True

    def find_provisioning_state_cluster_size(self):
        return self._find_cluster_provision_state(), self._find_cluster_size()

    def _find_cluster_size(self):
        print("finding cluster size")
        if self.cloud_details[self._PROPERTIES] is None and self.cloud_details[self._PROPERTIES][
            'managementCluster'] is None and \
                self.cloud_details[self._PROPERTIES]['managementCluster']['clusterSize'] is None:
            raise ManagementClusterNotFound("cluster size not found")
        cluster_size = self.cloud_details[self._PROPERTIES]['managementCluster']['clusterSize']
        return cluster_size

    def _find_cluster_provision_state(self):
        print("finding provisioning state")
        if self.cloud_details[self._PROPERTIES] is None and self.cloud_details[self._PROPERTIES][
            'managementCluster'] is None and \
                self.cloud_details[self._PROPERTIES]['managementCluster']['provisioningState'] is None:
            raise ManagementClusterNotFound("provisioning state details not found")
        provisioning_state = self.cloud_details[self._PROPERTIES]['managementCluster']['provisioningState']
        return provisioning_state

    def find_vnet_ip_cidr(self):
        if self.cloud_details[self._PROPERTIES] is None and self.cloud_details[self._PROPERTIES]['networkBlock'] is None:
            raise VNETIPCIDRNotFound("ip cidr not found in cloud details")
        return self.cloud_details[self._PROPERTIES]['networkBlock']

    def find_cluster_location(self):
        if self.cloud_details[self._LOCATION] is None:
            raise Exception("invalid cloud details. location not present")
        return self.cloud_details[self._LOCATION]

