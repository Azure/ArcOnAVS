
#
# @author shrohilla
#
class AzCli:
    az_command = "az"
    def __init__(self):
        self.az_command = "az"
        self.az_args = []

    def az_args(self):
        return self.az_args

    def append(self, value):
        self.az_args.append(value)
        return self

    def build_az_cli(self):
        str_az_cmd = self.az_command
        str_az_cmd = str_az_cmd+" " + " ".join(self.az_args)
        return str_az_cmd