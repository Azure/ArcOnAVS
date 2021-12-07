#!/usr/bin/python

from ._utils import TempChangeDir, bytes_to_string, create_dir_if_doesnot_exist
import subprocess, os
import logging

_govc_binary_dir = '.temp'

def govc_cli(*args):
    create_dir_if_doesnot_exist(_govc_binary_dir)
    with TempChangeDir(_govc_binary_dir):
        args = ' '.join(args)
        res = None
        try:
            cmd = os.path.join('.', 'govc')
            cmd = cmd + ' ' + args
            res = subprocess.check_output(cmd, shell=True)
            res = bytes_to_string(res)
        except Exception as e:
            logging.info(e)
            return res, 1
        return res, 0
