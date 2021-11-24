from base64 import b64decode
import os
from collections import deque
from time import sleep
from typing import Any
import uuid
from datetime import datetime, timedelta

def get_vm_snapshot_name(vm_template_name):
    return f'{vm_template_name}-snapshot'

def get_value_using_path_in_dict(dict_obj: dict, path: str):
    path_list = str.split(path, '.')
    value = dict_obj
    for k in path_list:
        if value is None:
            raise KeyError
        value = value[k]
    return value

def set_value_using_path_in_dict(dict_obj: dict, path: str, value):
    path_list = str.split(path, '.')
    while len(path_list) > 1:
        k = path_list.pop(0)
        dict_obj = dict_obj[k]
    dict_obj[path_list[0]] = value

def delete_unassigned_fields(dict_obj: dict):
    new_dict={}
    for k, v in dict_obj.items():
        if type(v) == dict:
            new_dict[k] = delete_unassigned_fields(v)
        elif v != "...":
            new_dict[k] = v
    return new_dict

def delete_empty_sub_dicts(dict_obj: dict):
    st = []
    q = deque()

    vals = [(dict_obj, k) for k in dict_obj]
    for val in vals:
        if type(val[0][val[1]]) == dict:
            q.append(val)
            st.append(val)

    while len(q) > 0:
        x = q.popleft()
        if type(x[0][x[1]]) == dict:
            vals = [(x[0][x[1]], k) for k in x[0][x[1]]]
            for val in vals:
                if type(val[0][val[1]]) == dict:
                    q.append(val)
                    st.append(val)
    while len(st) > 0:
        x = st.pop()
        if len(x[0][x[1]]) <= 0:
            try:
                del x[0][x[1]]
            except KeyError:
                pass

def bytes_to_string(b: bytes) -> str:
    return b.decode('UTF-8', errors='strict')

def string_to_bytes(s: str) -> bytes:
    return s.encode('UTF-8', errors='strict')

def decode_base64(data: str, altchars: bytes=None) -> str:
    return bytes_to_string(b64decode(string_to_bytes(data), altchars=altchars))

def confirm_prompt(msg):
    while True:
        print(msg)
        val = input('Y/N ?')
        val = str.lower(val).strip()
        if val in ['y', 'yes', 'n', 'no']:
            return val in ['y', 'yes']

def wait_until(callback, expected: Any, timeout: timedelta, frequency: timedelta = timedelta(seconds=10)):
    now = datetime.utcnow()
    endtime = now + timeout
    while datetime.utcnow() <= endtime:
        res = callback()
        if res is not None and expected.__eq__(res):
            return
        sleep(frequency.total_seconds())
    raise TimeoutError()

class TempChangeDir(object):
    def __init__(self, dir) -> None:
        self._prev = os.getcwd()
        self._new = dir

    def __enter__(self):
        os.chdir(self._new)

    def __exit__(self, *args, **kwargs):
        os.chdir(self._prev)

def generate_random_uuid():
    return str(uuid.uuid4())

def create_dir_if_doesnot_exist(path: str):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass