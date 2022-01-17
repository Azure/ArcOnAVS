import json
import logging

from ....executor.azcli._AzCliExecutor import AzCliExecutor
from ....constants import Constant
from ....entity.AzCli import AzCli
from ....entity.CustomerResource import CustomerResource
from ....entity.request._segment_request import SegmentRequest
from ....exception import InvalidDataException


class NSXSegmentHelper:
    _list_segment_url = Constant.NSX_MGMT_URL + "/segments?"+Constant.API_VERSION+"="+Constant.STABLE_API_VERSION_VALUE

    def __init__(self):
        self.az_cli_executor = AzCliExecutor()

    def get_segment_list(self, subscription_id, rg, private_cloud):
        list_segment_url = self._list_segment_url.format(subscription_id, rg, private_cloud)
        az_cli = AzCli().append(Constant.REST).append("-m").append(Constant.GET).append("-u") \
            .append(list_segment_url)
        return self.az_cli_executor.run_az_cli(az_cli)

    def retrieve_gateway(self, result):
        if len(result["value"]) < 1:
            raise InvalidDataException("segment size can't be less than 1")
        return result["value"][0]["properties"]["connectedGateway"]

    def _get_arc_segment_if_exists(self, result, segment_name):
        list_segment = result["value"]
        for segment in list_segment:
            if segment["name"].casefold() == segment_name.casefold():
                return segment
        return None
    
    def _are_no_ports_occupied_in_segment(self, segment):
        return len(segment["properties"].get("portVif", [])) == 0

    def create_segment(self, segment_request: SegmentRequest, customer_res: CustomerResource):
        create_segment_uri = self._create_segment_uri.format(customer_res.subscription_id,
                                                             customer_res.resource_group,
                                                             customer_res.private_cloud,
                                                             segment_request.display_name)
        az_cli = AzCli().append(Constant.RESOURCE).append(Constant.CREATE).append("--id") \
            .append(create_segment_uri).append("--properties").append(json.dumps(segment_request)) \
            .append(Constant.API_VERSION_DOUBLE_DASH).append(Constant.STABLE_API_VERSION_VALUE)
        res = self.run_az_cli(az_cli)
        logging.info("response for create segment :: ", res)
        return json.loads(res)
