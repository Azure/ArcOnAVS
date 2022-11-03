#!/usr/bin/python

# These are the exceptions used across different modules.

class FilePathNotFoundInArgs(Exception): pass

class InvalidConfigError(Exception): pass

class AzCommandError(Exception): pass

class InvalidOperation(Exception): pass

class ProgramExit(Exception): pass

class vCenterOperationFailed(Exception): pass

class InvalidInputError(Exception): pass

class OperationTimedoutError(Exception): pass

class InvalidState(Exception): pass

class ArmFeatureNotRegistered(Exception): pass


class ClusterExtensionCreationFailed(Exception): pass

class ArmProviderNotRegistered(Exception): pass

class InvalidRegion(Exception): pass

class InternetNotEnabled(Exception): pass
