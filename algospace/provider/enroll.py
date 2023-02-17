#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 注册算法
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2023-02-17 14:09:09
'''

from .config import enroll_url, verify_config_url, is_component_normal_url
import requests
import time
import traceback
from algospace.login import login, login_instance
from algospace.logger import algospace_logger
from .config_loader import ConfigLoader


def enroll_from_config(config_path: str):
    ''' 从配置文件注册 '''
    try:
        algorithm_config = ConfigLoader(config_path)
        algospace_logger.info('Login...')
        if not login(secret=algorithm_config.secret, username=algorithm_config.username, password=algorithm_config.password, privilege='PROVIDER'):
            algospace_logger.error('Login failed. Please check your secret or password.')
            exit(1)
        algospace_logger.info('Enroll processing...')
        enroll(algorithm_config.name, algorithm_config.version, algorithm_config.service_input, algorithm_config.service_output,
               algorithm_config.description, algorithm_config.scope, algorithm_config.chinese_name, algorithm_config.document, algorithm_config.config_file_content)
        algospace_logger.info(
            f'Enroll successfully! Name: {algorithm_config.name}, Version: {algorithm_config.version}')
    except Exception as e:
        traceback.print_exc()
        algospace_logger.error(f'Enroll error: {str(e)}')
        exit(1)


def enroll(name: str, version: str, input: dict, output: dict, description: str, scope: str, chinese_name: str, document: str, config_file: str):
    ''' 注册算法 '''
    enroll_data = {
        'name': name,
        'version': version,
        'input_param': [{
            'key': key,
            'type': val['type'],
            'describe': val['describe'],
            **({'max_length': val.get('max_length')} if val.get('max_length') is not None else {}),
            **({'max_value': val.get('max_value')} if val.get('max_value') is not None else {}),
            **({'min_value': val.get('min_value')} if val.get('min_value') is not None else {}),
            **({'max_fraction': val.get('max_fraction')} if val.get('max_fraction') is not None else {}),
            **({'max_size': val.get('max_size')} if val.get('max_size') is not None else {}),
        } for key, val in input.items()],
        'output_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in output.items()],
        'description': description,
        'scope': scope,
        'chinese_name': chinese_name,
        'document': document,
        'config_file': config_file
    }
    headers = login_instance.get_header()
    resp = requests.post(enroll_url, json=enroll_data, headers=headers)
    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception(resp.status_code, resp.content.decode())
    if resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Enroll algorithm error.'))
    return True


def verify_config(name: str, version: str, input: dict, output: dict):
    ''' 校验算法配置 '''
    enroll_data = {
        'name': name,
        'version': version,
        'input_param': [{
            'key': key,
            'type': val['type'],
            'describe': val['describe'],
            **({'max_length': val.get('max_length')} if val.get('max_length') is not None else {}),
            **({'max_value': val.get('max_value')} if val.get('max_value') is not None else {}),
            **({'min_value': val.get('min_value')} if val.get('min_value') is not None else {}),
            **({'max_fraction': val.get('max_fraction')} if val.get('max_fraction') is not None else {}),
            **({'max_size': val.get('max_size')} if val.get('max_size') is not None else {}),
        } for key, val in input.items()],
        'output_param': [{'key': key, 'type': val['type'], 'describe': val['describe']} for key, val in output.items()]
    }
    headers = login_instance.get_header()
    resp = requests.post(verify_config_url, json=enroll_data, headers=headers)
    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception(resp.status_code, resp.content.decode())
    if resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Verify algorithm config error.'))
    file = resp.json()['data'].get('file')
    if file is not None:
        return file
    else:
        return ''


def is_component_normal(name: str, version: str):
    ''' 获取算法转发组件状态正常 '''
    headers = login_instance.get_header()
    resp = requests.get(is_component_normal_url,
                        params={'name': name, 'version': version},
                        headers=headers)
    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception(resp.status_code, resp.content.decode())
    if resp.json()['status'] != 200:
        raise Exception(resp.json().get('err_msg', 'Get component status error.'))
    is_component_normal = resp.json()['data'].get('is_component_normal')
    ask_data_url = resp.json()['data'].get('ask_data_url')
    ws_ask_data_url = resp.json()['data'].get('ws_ask_data_url')
    return_ans_url = resp.json()['data'].get('return_ans_url')
    return_err_url = resp.json()['data'].get('return_err_url')
    gradio_upload_url = resp.json()['data'].get('gradio_upload_url')
    return {
        'is_component_normal': is_component_normal,
        'ask_data_url': ask_data_url,
        'ws_ask_data_url': ws_ask_data_url,
        'return_ans_url': return_ans_url,
        'return_err_url': return_err_url,
        'gradio_upload_url': gradio_upload_url,
    }
