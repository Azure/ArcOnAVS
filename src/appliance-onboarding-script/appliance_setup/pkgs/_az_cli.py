#!/usr/bin/python

# This module is wrapper around az cli command execution
# az_cli and az_cli_with_retries are two functions which
# can be used to execute az commands.

import os, subprocess, logging
from ._utils import bytes_to_string

def az_cli (*args):
    res = None
    try:
        cmd = 'az ' + ' '.join(args)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            cmd = cmd + ' --debug'
        logging.debug(f'Executing command {cmd}')
        res = subprocess.check_output(cmd, shell=True)
        res = bytes_to_string(res)
    except Exception as e:
        logging.error(e)
        return res, 1
    return res, 0
