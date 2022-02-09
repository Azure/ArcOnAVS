import json
import logging
import sys

from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...creator.creator import Creator
from ...entity.AzCli import AzCli
from ...exception import ArcAddOnCreationException
from ...entity.CustomerResource import CustomerResource
from ...entity.request.arc_addon_request import ArcAddonRequest


class ArcAddonCreator(Creator):
    _create_arc_addon = Constant.PRIVATE_CLOUD_URL + "/addons/arc"

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()

    def create(self, *args):
        customer_res: CustomerResource = args[0]
        arc_addon_data: ArcAddonRequest = args[1]
        create_arc_addon_uri = self._create_arc_addon.format(customer_res.subscription_id, customer_res.resource_group,
                                                   customer_res.private_cloud)
        json_data = json.dumps(json.dumps(arc_addon_data.__dict__))
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_arc_addon_uri).append("--properties").append(json_data) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.PREVIEW_API_VERSION_VALUE)
        get_az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_arc_addon_uri)
        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            logging.info("Created arc addon")
            res = self._az_cli_executor.run_az_cli(get_az_cli)
        except Exception as e:
            raise ArcAddOnCreationException("Exception occured while creating arc addon!") from e
        return res
