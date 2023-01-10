#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-24 14:45:40
@LastEditors: Kermit
@LastEditTime: 2023-01-09 23:23:17
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
upload_code_url = 'https://algospace.top/core/algo/builder/file'


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
