import logging
import sys

from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...deleter.deleter import Deleter
from ...entity.AzCli import AzCli
from ...exception import ArcAddOnDeletionException
from ...entity.CustomerResource import CustomerResource


class ArcAddonDeleter(Deleter):
    _delete_arc_addon = Constant.PRIVATE_CLOUD_URL + "/addons/arc"

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()

    def delete(self, *args):
        customer_res: CustomerResource = args[0]
        delete_arc_addon_uri = self._delete_arc_addon.format(customer_res.subscription_id, customer_res.resource_group,
                                                             customer_res.private_cloud)
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.DELETE).append("--id") \
            .append(delete_arc_addon_uri) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.PREVIEW_API_VERSION_VALUE)
        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            logging.info("response for delete arc addon :: ", res)
        except Exception as e:
            raise ArcAddOnDeletionException("Exception occured while deleting arc addon!") from e
        return res
