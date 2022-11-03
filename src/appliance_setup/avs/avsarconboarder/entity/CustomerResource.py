class CustomerResource:
    def __new__(cls, rg, subscription_id, private_cloud, appliance_name, *args, **kwargs):
        cls.resource_group = rg
        cls.subscription_id = subscription_id
        cls.private_cloud = private_cloud
        cls.appliance_name = appliance_name
        return cls

