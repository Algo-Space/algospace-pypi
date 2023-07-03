#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-24 14:45:40
@LastEditors: Kermit
@LastEditTime: 2023-05-22 16:57:56
'''

wait_interval = 1
call_interval = 0.1


enroll_url = 'https://algospace.top/core/algo/pypi/enroll'
verify_config_url = 'https://algospace.top/core/algo/pypi/verify'
is_component_normal_url = 'https://algospace.top/core/algo/pypi/is_component_normal'
get_service_status_url = 'https://algospace.top/core/algo/pypi/cloud/status'
heartbeat_url = 'https://algospace.top/core/heartbeat/send'
storage_file_url = 'https://algospace.top/core/storage/file'
start_build_url = 'https://algospace.top/core/algo/build/start'
reset_status_url = 'https://algospace.top/core/algo/build/reset'
get_build_ws_url = 'wss://algospace.top/core/algo/build/ws/log'
start_deploy_url = 'https://algospace.top/core/algo/deploy/start'
get_deploy_ws_url = 'wss://algospace.top/core/algo/deploy/ws/log'
upload_code_url = 'https://ruc.algospace.top:4443/core/algo/builder/file'

input_param_str_max_length: int = 100000  # 输入参数的最大长度
input_param_image_max_size: int = 100  # 输入图片的最大大小(MB)
input_param_voice_max_size: int = 100  # 输入音频的最大大小(MB)
input_param_video_max_size: int = 500  # 输入视频的最大大小(MB)

input_param_str_default_max_length: int = 10000  # 输入参数的默认最大长度
input_param_image_default_max_size: int = 2  # 输入图片的默认最大大小(MB)
input_param_voice_default_max_size: int = 10  # 输入音频的默认最大大小(MB)
input_param_video_default_max_size: int = 20  # 输入视频的默认最大大小(MB)


class Algoinfo:
    def __init__(self, algorithm_name: str, algorithm_version: str):
        self.name = algorithm_name
        self.version = algorithm_version

    @property
    def full_name(self):
        return f'{self.name}_{self.version}'

    @property
    def lower_name(self):
        return self.full_name.replace('-', '_').replace('.',  '_').lower()

    @property
    def upper_name(self):
        return self.full_name.replace('-', '_').replace('.',  '_').upper()

    @property
    def image_name(self):
        return self.name.replace('@', '_').lower()  # 镜像的名称需要限制为 [a-z0-9], 其中可以出现的符号为 [-._]

    @property
    def image_version(self):
        return self.version.lower()  # 镜像的名称需要限制为 [a-z0-9], 其中可以出现的符号为 [-._]

    @property
    def algorithm_site(self):
        return f'https://algospace.top/algorithm/{self.name}/{self.version}'

    @property
    def algorithm_cloud_site(self):
        return self.algorithm_site + '/cloud'
