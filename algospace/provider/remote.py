#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-12-13 16:19:45
@LastEditors: Kermit
@LastEditTime: 2022-12-20 18:29:18
'''

from zipfile import ZipFile
import os
import requests
from .config_loader import ConfigLoader
from .config import Algoinfo
from algospace.login import login_instance


def upload_local_file_as_zip(config_path: str):
    ''' 以 zip 上传本地所有文件 '''
    root_path = os.getcwd()
    zip_name = 'algospace.zip'

    # 压缩工作目录所有文件和文件夹
    with ZipFile(zip_name, 'w') as zip_file:
        for root, _, files in os.walk(root_path):
            for file in files:
                if file == zip_name and root == root_path:
                    continue
                file_path = os.path.join(root, file)
                relative_path = file_path.replace(root_path, '')
                zip_file.write(file_path, relative_path)

    algorithm_config = ConfigLoader(config_path)
    algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)

    with open(zip_name, 'rb') as f:
        files = {'file': (zip_name, f.read())}
    response = requests.post(algorithm_info.upload_code_url, files=files, headers=login_instance.get_header())
    if response.status_code != 200 and response.status_code != 201:
        raise Exception(response.status_code, response.content.decode())
    if response.json()['status'] != 200:
        raise Exception(response.json().get('err_msg', 'Upload zip file error.'))


def start_build_image(config_path: str):
    ''' 开始构建镜像 '''
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
