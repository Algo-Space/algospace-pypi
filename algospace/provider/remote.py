#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-12-13 16:19:45
@LastEditors: Kermit
@LastEditTime: 2022-12-22 17:05:39
'''

import traceback
from websocket import create_connection
from zipfile import ZipFile
import os
import time
import requests
import json
from .config_loader import ConfigLoader
from .config import Algoinfo
from algospace.login import login_instance


def upload_local_file_as_zip(config_path: str):
    ''' 以 zip 上传本地所有文件 '''
    root_path = os.getcwd()
    zip_name = 'algospace.zip'
    try:
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Zip processing...')
        # 压缩工作目录所有文件和文件夹
        with ZipFile(zip_name, 'w') as zip_file:
            for root, _, files in os.walk(root_path):
                for file in files:
                    if file == zip_name and root == root_path:
                        continue
                    file_path = os.path.join(root, file)
                    relative_path = file_path.replace(root_path, '')
                    zip_file.write(file_path, relative_path)
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', f'[AlgoSpace] Zip successfully!')

        algorithm_config = ConfigLoader(config_path)
        algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)

        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Upload processing...')
        with open(zip_name, 'rb') as f:
            files = {'file': (zip_name, f.read())}
        response = requests.post(algorithm_info.upload_code_url, files=files, headers=login_instance.get_header())
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(response.status_code, response.content.decode())
        if response.json()['status'] != 200:
            raise Exception(response.json().get('err_msg', 'Upload zip file error.'))
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', f'[AlgoSpace] Upload successfully!')
    except Exception as e:
        traceback.print_exc()
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Upload error:', str(e))
        exit(1)
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)


def start_build_image(config_path: str):
    ''' 开始构建镜像 '''
    try:
        algorithm_config = ConfigLoader(config_path)
        algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)

        response = requests.post(algorithm_info.start_build_url, json={
            'algoname': algorithm_config.name,
            'version': algorithm_config.version,
            'config_path': config_path,  # TODO: 兼容 windows 路径格式
        }, headers=login_instance.get_header())
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(response.status_code, response.content.decode())
        if response.json()['status'] != 200:
            raise Exception(response.json().get('err_msg', 'Start build image error.'))
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Start build...')
    except Exception as e:
        traceback.print_exc()
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Start build error:', str(e))
        exit(1)


def get_build_log(config_path: str):
    ''' 获取构建日志 '''
    algorithm_config = ConfigLoader(config_path)
    algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)
    last_log_row_num = 0

    ws = create_connection(algorithm_info.get_build_ws_url, header=login_instance.get_header())
    ws.send(json.dumps({
        'algoname': algorithm_config.name,
        'version': algorithm_config.version,
        'last_log_row_num': last_log_row_num,
    }))

    while ws.connected:
        message = ws.recv()
        if not message:
            continue
        result = json.loads(message)
        last_log_row_num = result['last_log_row_num']
        print(result['log'])


def start_deploy(config_path: str):
    ''' 开始部署 '''
    try:
        algorithm_config = ConfigLoader(config_path)
        algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)

        response = requests.post(algorithm_info.start_deploy_url, json={
            'algoname': algorithm_config.name,
            'version': algorithm_config.version,
        }, headers=login_instance.get_header())
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(response.status_code, response.content.decode())
        if response.json()['status'] != 200:
            raise Exception(response.json().get('err_msg', 'Start deploy error.'))
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Start deploy...')
    except Exception as e:
        traceback.print_exc()
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Start deploy error:', str(e))
        exit(1)


def get_deploy_log(config_path: str):
    ''' 获取部署日志 '''
    algorithm_config = ConfigLoader(config_path)
    algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)
    last_log_row_num = 0

    ws = create_connection(algorithm_info.get_deploy_ws_url, header=login_instance.get_header())
    ws.send(json.dumps({
        'algoname': algorithm_config.name,
        'version': algorithm_config.version,
        'last_log_row_num': last_log_row_num,
    }))

    while ws.connected:
        message = ws.recv()
        if not message:
            continue
        result = json.loads(message)
        last_log_row_num = result['last_log_row_num']
        print(result['log'])
