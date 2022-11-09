#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 注册算法
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2022-11-09 18:54:30
'''

from .config import enroll_url, verify_config_url, is_component_normal_url
import requests
from vsource.login import login_instance


def enroll(name: str, version: str, input: dict, output: dict, config_file: str):
    ''' 注册算法 '''
    enroll_data = {
        'name': name,
        'version': version,
        'input_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in input.items()],
        'output_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in output.items()],
        'config_file': config_file
    }
    headers = login_instance.get_header()
    resp = requests.post(enroll_url, json=enroll_data, headers=headers)
    if resp.status_code != 200 and resp.status_code != 201 and resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Enroll algorithm error.'))
    return True


def verify_config(name: str, version: str, input: dict, output: dict):
    ''' 校验算法配置 '''
    enroll_data = {
        'name': name,
        'version': version,
        'input_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in input.items()],
        'output_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in output.items()]
    }
    headers = login_instance.get_header()
    resp = requests.post(verify_config_url, json=enroll_data, headers=headers)
    if resp.status_code != 200 and resp.status_code != 201 and resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Verify algorithm config error.'))
    file = resp.json()['data'].get('file')
    if file is not None:
        return file
    else:
        return ''


def is_component_normal(name: str, version: str):
    ''' 获取算法转发组件状态正常 '''
    headers = login_instance.get_header()
    resp = requests.get(f'{is_component_normal_url}?name={name}&version={version}', headers=headers)
    if resp.status_code != 200 and resp.status_code != 201 and resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Get component status error.'))
    is_component_normal = resp.json()['data'].get('is_component_normal')
    return is_component_normal
