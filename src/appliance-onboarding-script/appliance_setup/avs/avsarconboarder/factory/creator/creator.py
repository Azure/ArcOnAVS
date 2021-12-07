from ...creator.dhcp.dhcp_creator import DHCPCreator
from ...creator.dns.dns_creator import DNSZoneCreator, DNSServiceCreator
from ...creator.file.file_creator import FileCreator
from ...creator.segment.segment_creator import SegmentCreator
from ...creator.type.creator_type import CreatorType
from ...exception import UnexpectedCreatorException
from ...factory.absfact import ArcAbsFactory


class CreatorFactory(ArcAbsFactory):
    instance_map = {}

    def retrieve_instance(self, *args):
        creator_type = args[0][0]
        if self.instance_map[creator_type] is not None:
            return self.instance_map[creator_type]
        raise UnexpectedCreatorException("creator type is not found")

    def build_factory(self, *args):
        for creator_type in CreatorType:
            creator: creator = None
            if creator_type == CreatorType.dhcp:
                creator = DHCPCreator()
            elif creator_type == CreatorType.segment:
                creator = SegmentCreator()
            elif creator_type == CreatorType.file:
                creator = FileCreator()
            elif creator_type == CreatorType.dns_zone:
                creator = DNSZoneCreator()
            elif creator_type == CreatorType.dns_service:
                creator = DNSServiceCreator()

            self.instance_map[creator_type] = creator


factory_instance = None


def get_instance():
    if factory_instance is None:
        instance = CreatorFactory()
        instance.build_factory()
    return instance