#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-12-13 16:19:45
@LastEditors: Kermit
@LastEditTime: 2023-02-22 16:22:07
'''

import traceback
import websocket
from zipfile import ZipFile
import os
import time
import requests
from requests_toolbelt import MultipartEncoder
import json
from .config_loader import ConfigLoader
from .config import Algoinfo, get_service_status_url, start_build_url, reset_status_url, get_build_ws_url, start_deploy_url, get_deploy_ws_url, upload_code_url
from algospace.login import login_instance, login
from algospace.provider.enroll import enroll
from algospace.logger import algospace_logger


def run_cloud_deploy(config_path: str, reset: bool = False):
    ''' 云端部署 '''
    algospace_logger.info('Initializing...')
    algorithm_config = ConfigLoader(config_path)
    algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)
    if not login(secret=algorithm_config.secret, username=algorithm_config.username, password=algorithm_config.password, privilege='PROVIDER'):
        algospace_logger.error('Login failed. Please check your secret or password.')
        exit(1)

    try:
        enroll(algorithm_config.name,
               algorithm_config.version,
               algorithm_config.service_input,
               algorithm_config.service_output,
               algorithm_config.description,
               algorithm_config.scope,
               algorithm_config.chinese_name,
               algorithm_config.document,
               algorithm_config.config_file_content)
    except Exception as e:
        algospace_logger.error(f'Enroll failed: {str(e)}')
        exit(1)

    if reset and get_service_status(algorithm_config.name, algorithm_config.version) == 'built':
        try:
            reset_status_image(algorithm_config.name, algorithm_config.version)
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Reset status error: {str(e)}')
            exit(1)

    if get_service_status(algorithm_config.name, algorithm_config.version) == 'unready':
        try:
            algospace_logger.info('Upload processing...')
            algospace_logger.info('It may take a few minutes to upload your code.')
            algospace_logger.info('It depends on the size of your code.')
            upload_local_file_as_zip(algorithm_config.name, algorithm_config.version)
            algospace_logger.info('Upload successfully!')
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Upload error: {str(e)}')
            exit(1)

        try:
            start_build_image(algorithm_config.name, algorithm_config.version, config_path)
            algospace_logger.info('Start build...')
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Start build error: {str(e)}')
            exit(1)

    if get_service_status(algorithm_config.name, algorithm_config.version) in ('built', 'building', 'pending', 'unready'):
        try:
            algospace_logger.info('Build log:')
            get_build_log(algorithm_config.name, algorithm_config.version)
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Get build log error: {str(e)}')
            exit(1)

        while get_service_status(algorithm_config.name, algorithm_config.version) in ('building', 'pending'):
            time.sleep(1)
        if get_service_status(algorithm_config.name, algorithm_config.version) == 'unready':
            algospace_logger.error('Build failed.')
            algospace_logger.error('Please check your code and config file according to the build log.')
            algospace_logger.error('After modification, please run `algospace cloud:deploy` again.')
            algospace_logger.error(
                f'Or go to {algorithm_info.algorithm_cloud_site} to replace part of files uploaded. (Avoid re-uploading the entire code)')
            exit(1)
        if get_service_status(algorithm_config.name, algorithm_config.version) == 'built':
            algospace_logger.info('Build successfully!')

    if get_service_status(algorithm_config.name, algorithm_config.version) == 'built':
        try:
            start_deploy(algorithm_config.name, algorithm_config.version)
            algospace_logger.info('Start deploy...')
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Start deploy error: {str(e)}')
            exit(1)

    if get_service_status(algorithm_config.name, algorithm_config.version) in ('deployed', 'deploying', 'waiting', 'built'):
        try:
            algospace_logger.info('It may take a few minutes to distribute the image to calculation node.')
            algospace_logger.info('And then the deploy log will be shown below. Please wait patiently.')
            algospace_logger.info('Deploy log:')
            get_deploy_log(algorithm_config.name, algorithm_config.version)
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Get deploy log error: {str(e)}')
            exit(1)

        while get_service_status(algorithm_config.name, algorithm_config.version) in ('deploying', 'waiting'):
            time.sleep(1)
        if get_service_status(algorithm_config.name, algorithm_config.version) == 'built':
            algospace_logger.error('Deploy failed.')
            algospace_logger.error('Please check your code and config file according to the deploy log.')
            algospace_logger.error('After modification, please run `algospace cloud:deploy --reset` to deploy again.')
            algospace_logger.error(
                f'Or go to {algorithm_info.algorithm_cloud_site} to replace part of files uploaded. (Avoid re-uploading the entire code)')
            exit(1)
        if get_service_status(algorithm_config.name, algorithm_config.version) == 'deployed':
            algospace_logger.info('Deploy successfully!')
            algospace_logger.info('You can run `algospace cloud:log` to view the running log.')


def show_running_log(config_path: str):
    ''' 显示运行日志 '''
    algorithm_config = ConfigLoader(config_path)
    if not login(secret=algorithm_config.secret, username=algorithm_config.username, password=algorithm_config.password, privilege='PROVIDER'):
        algospace_logger.error('Login failed. Please check your secret or password.')
        exit(1)

    if get_service_status(algorithm_config.name, algorithm_config.version) == 'deployed':
        try:
            get_deploy_log(algorithm_config.name, algorithm_config.version, True)
        except Exception as e:
            traceback.print_exc()
            algospace_logger.error(f'Get running log error: {str(e)}')
            exit(1)
    else:
        algospace_logger.warning('The service is not deployed. Please run `algospace cloud:deploy` first.')


def get_service_status(name: str, version: str):
    ''' 获取服务状态 '''
    response = requests.get(get_service_status_url,
                            params={'algoname': name, 'version': version},
                            headers=login_instance.get_header())
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(response.status_code, response.content.decode())
    if response.json()['status'] != 200:
        raise Exception(response.json().get('err_msg', 'Get service status error.'))
    return response.json()['data']['status']


def upload_local_file_as_zip(name: str, version: str):
    ''' 以 zip 上传本地所有文件 '''
    root_path = os.getcwd()
    zip_name = 'algospace.zip'
    try:
        # 压缩工作目录所有文件和文件夹
        with ZipFile(zip_name, 'w') as zip_file:
            for root, _, files in os.walk(root_path):
                for file in files:
                    if file == zip_name and root == root_path:
                        continue
                    file_path = os.path.join(root, file)
                    relative_path = file_path.replace(root_path, '')
                    zip_file.write(file_path, relative_path)

        with open(zip_name, 'rb') as f:
            data = {'file': (zip_name, f)}
            m = MultipartEncoder(fields=data)
            response = requests.post(f'{upload_code_url}/{name}/{version}',
                                     data=m,
                                     headers={'Content-Type': m.content_type, **login_instance.get_header()})
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(response.status_code, response.content.decode())
        if response.json()['status'] != 200:
            raise Exception(response.json().get('err_msg', 'Upload zip file error.'))
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)


def start_build_image(name: str, version: str, config_path: str):
    ''' 开始构建镜像 '''
    response = requests.post(start_build_url, json={
        'algoname': name,
        'version': version,
        'config_path': config_path,  # TODO: 兼容 windows 路径格式
    }, headers=login_instance.get_header())
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(response.status_code, response.content.decode())
    if response.json()['status'] != 200:
        raise Exception(response.json().get('err_msg', 'Start build image error.'))


def reset_status_image(name: str, version: str):
    ''' 重置算法状态 '''
    response = requests.post(reset_status_url, json={
        'algoname': name,
        'version': version,
    }, headers=login_instance.get_header())
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(response.status_code, response.content.decode())
    if response.json()['status'] != 200:
        raise Exception(response.json().get('err_msg', 'Reset status error.'))


def get_build_log(name: str, version: str, last_log_row_num: int = 0):
    ''' 获取构建日志 '''
    def on_message(ws: websocket.WebSocket, message):
        nonlocal last_log_row_num
        result = json.loads(message)
        last_log_row_num = result['last_log_row_num']
        print(add_prefix_to_log(result['log'], 'Cloud Build Log'))

    def on_close(ws: websocket.WebSocket, close_status_code: int, close_msg: str):
        if close_status_code and close_status_code != 1000 and close_status_code < 4000:
            # 非应用的异常码则重新连接
            get_build_log(name, version, last_log_row_num)
        elif close_status_code != 1000:
            print(f'Get log error: {close_status_code} {close_msg}')

    def on_open(ws: websocket.WebSocket):
        ws.send(json.dumps({
            'algoname': name,
            'version': version,
            'last_log_row_num': last_log_row_num,
        }))

    ws = websocket.WebSocketApp(get_build_ws_url,
                                header=login_instance.get_header(),
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close)
    ws.run_forever()


def start_deploy(name: str, version: str):
    ''' 开始部署 '''
    response = requests.post(start_deploy_url, json={
        'algoname': name,
        'version': version,
    }, headers=login_instance.get_header())
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(response.status_code, response.content.decode())
    if response.json()['status'] != 200:
        raise Exception(response.json().get('err_msg', 'Start deploy error.'))


def get_deploy_log(name: str, version: str, keep_after_success: bool = False, last_log_row_num: int = 0):
    ''' 获取部署日志 '''

    def on_message(ws: websocket.WebSocket, message):
        nonlocal last_log_row_num
        # websocket-client 限制消息体大小 64kb，需要注意
        result = json.loads(message)
        if result['is_cover_previous']:
            print(f'\033[{last_log_row_num}A\r', end='')
        last_log_row_num = result['last_log_row_num']
        print(add_prefix_to_log(result['log'], 'Cloud Deploy Log'))

    def on_close(ws: websocket.WebSocket, close_status_code: int, close_msg: str):
        if close_status_code and close_status_code != 1000 and close_status_code < 4000:
            # 非应用的异常码则重新连接
            get_deploy_log(name, version, keep_after_success, last_log_row_num)
        elif close_status_code != 1000:
            print(f'Get log error: {close_status_code} {close_msg}')

    def on_open(ws: websocket.WebSocket):
        ws.send(json.dumps({
            'algoname': name,
            'version': version,
            'keep_after_success': True if keep_after_success else '',
            'last_log_row_num': last_log_row_num,
        }))

    ws = websocket.WebSocketApp(get_deploy_ws_url,
                                header=login_instance.get_header(),
                                on_open=on_open,
                                on_message=on_message,
                                on_close=on_close)
    ws.run_forever()


def add_prefix_to_log(log: str, prefix: str):
    ''' 给日志添加前缀 '''
    log_list = log.split('\n')
    return '\n'.join(map(lambda x: f'[{prefix}] {x}', log_list))
