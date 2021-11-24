class UnknownPathException(Exception):
    pass


class ValidationFailedException(Exception):
    pass


class InvalidDataException(Exception):
    pass


class ValidationFailedException(Exception):
    pass


class UnexpectedRetrievalException(Exception):
    pass


class VCSADetailsNotFoundException(Exception):
    pass


class InternetEnabledFlagNotFound(Exception):
    pass


class CustomerDetailsNotFound(Exception):
    pass


class ManagementClusterNotFound(Exception):
    pass


class UnExpectedError(Exception):
    pass


class UnexpectedCreatorException(Exception):
    pass


class SegmentDHCPRangeError(Exception):
    pass


class VNETIPCIDRNotFound(Exception):
    pass


class InvalidInputError(Exception):
    pass


class DataNotFoundException(Exception):
    pass


class AlreadyExistsException(Exception):
    pass


class PortsAlreadyOccupiedInSegmentException(Exception):
    pass


class CreationException(Exception):
    pass


class DHCPCreationException(CreationException):
    pass


class DNSZoneCreationException(CreationException):
    pass


class DNSServerCreationException(CreationException):
    pass


class SegmentCreationException(CreationException):
    pass


class ArcAddOnCreationException(CreationException):
    pass


class DeletionException(Exception):
    pass


class ArcAddOnDeletionException(DeletionException):
    pass