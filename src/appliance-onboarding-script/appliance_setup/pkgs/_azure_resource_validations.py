import json
import logging
from ._az_cli import az_cli
from ._utils import wait_until
from datetime import timedelta
from ._exceptions import OperationTimedoutError

def _wait_until_appliance_is_in_running_state(config: dict):
    logging.info(f'Waiting until Appliance is in RUNNING state.')
    resource_group = config['resourceGroup']
    appliance_name = config['nameForApplianceInAzure']
    def wrapper():
        res, err = az_cli('arcappliance', 'show',
            '--resource-group', f'"{resource_group}"',
            '--name', f'"{appliance_name}"'
        )
        if not err:
            res = json.loads(res)
            state = res['status']
            logging.info(f'Appliance is in {state} state.')
            return state
        logging.error('Get appliance operation failed.')
    try:
        wait_until(wrapper, 'Running', timedelta(minutes=10), frequency=timedelta(seconds=30))
        logging.info(f'Appliance is in RUNNING state.')
    except TimeoutError:
        raise OperationTimedoutError(f'Timeout occured while waiting for Appliance to be in RUNNING state.')