from ...creator.type.creator_type import CreatorType
from ...entity._segmentData import SegmentData
from ...entity.request._segment_request import SegmentRequest
from ...exception import AlreadyExistsException
from ...factory.creator import creator
from ...processor._processor import Processor
from ...creator.creator import Creator
from ...processor.nsx.helper import _NSXSegmentHelper
from ...entity.CustomerResource import CustomerResource


class SegmentProcessor(Processor):

    def __init__(self, customer_res: CustomerResource, segment_data: SegmentData):
        self.url = None
        self._segment_helper = _NSXSegmentHelper.NSXSegmentHelper()
        self._customer_res = customer_res
        self._segment_data = segment_data
        self._segment_creator: Creator = creator.get_instance().retrieve_instance([CreatorType.segment])

    def validate(self):
        arc_segment = self._segment_helper._get_arc_segment_if_exists(self._segment_list, self._segment_data.segment_name)
        if arc_segment:
            raise AlreadyExistsException('segment ({}) already exists!'.format(self._segment_data.segment_name))
        return True

    def pre_process(self):
        res = self._segment_helper.get_segment_list(self._customer_res.subscription_id, self._customer_res.resource_group,
                                                    self._customer_res.private_cloud)
        print('res in pre_process in segment processor :: ', res)
        self._tnt_gw = self._segment_helper.retrieve_gateway(res)
        self._segment_list = res
        Processor.pre_process(self)

    def execute_process(self):
        segment_req = self.build_segment_request()

        args = [self._customer_res, segment_req]
        res = self._segment_creator.create(args)
        print("segment created successfully :: ",res)

    def build_segment_request(self):
        subnet_details = {"dhcpRanges": self._segment_data.dhcp_range,
                          "gatewayAddress": self._segment_data.gateway_ip_cidr
                          }
        segment_req = SegmentRequest(
            displayName=self._segment_data.segment_name,
            connectedGateway=self._tnt_gw,
            subnet=subnet_details,
            revision=0
        )
        return segment_req
