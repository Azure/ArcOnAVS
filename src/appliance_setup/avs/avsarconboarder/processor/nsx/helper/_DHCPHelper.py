from ....executor.azcli._AzCliExecutor import AzCliExecutor
from ....constants import Constant
from ....entity.AzCli import AzCli
from ....exception import ValidationFailedException


class DHCPHelper:
    _list_dhcp_url = Constant.NSX_MGMT_URL + "/dhcpConfigurations?"+Constant.API_VERSION+"="+Constant.STABLE_API_VERSION_VALUE
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.az_cli_executor = AzCliExecutor()
            cls.instance = object.__new__(cls)
        return cls.instance

    def retrieve_dhcp_server(self, subscription_id, rg, private_cloud):
        list_dhcp_url = self._list_dhcp_url.format(subscription_id, rg, private_cloud)
        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u").\
            append(list_dhcp_url)
        return self.az_cli_executor.run_az_cli(az_cli)

    def find_dhcp_server_count(self, dhcp_server_list: object):
        if dhcp_server_list is None:
            raise ValidationFailedException("dhcp server list can not be null")

        return len(dhcp_server_list["value"])
