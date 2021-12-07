import json

from ...executor.azcli._AzCliExecutor import AzCliExecutor
from ...constants import Constant
from ...entity.AzCli import AzCli
from ...exception import SegmentCreationException
from ...entity.CustomerResource import CustomerResource
from ...entity.request._segment_request import SegmentRequest
from ...creator.creator import Creator


class SegmentCreator(Creator):

    _create_segment_uri = Constant.NSX_SUBSCRIPTION_URI+"/segments/{3}"

    def __init__(self):
        self._az_cli_executor = AzCliExecutor()

    def create(self, *args):
        customer_res: CustomerResource = args[0][0]
        segment_request: SegmentRequest = args[0][1]
        create_segment_uri = self._create_segment_uri.format(customer_res.subscription_id,
                                                             customer_res.resource_group,
                                                             customer_res.private_cloud,
                                                             segment_request.displayName)

        json_data = json.dumps(json.dumps(segment_request.__dict__))
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_segment_uri).append("--properties").append(json_data) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.STABLE_API_VERSION_VALUE)
        res = None
        try:
            res = self._az_cli_executor.run_az_cli(az_cli)
            print("response for create segment :: ", res)
        except Exception as e:
            raise SegmentCreationException("Exception occured while creating segment!") from e
        return res
