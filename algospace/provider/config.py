#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-24 14:45:40
@LastEditors: Kermit
@LastEditTime: 2022-12-29 18:53:44
'''

wait_interval = 1
call_interval = 0.1


enroll_url = 'https://algospace.top/core/algo/pypi/enroll'
verify_config_url = 'https://algospace.top/core/algo/pypi/verify'
is_component_normal_url = 'https://algospace.top/core/algo/pypi/is_component_normal'


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
    def heartbeat_url(self):
        return 'https://algospace.top/core/heartbeat/send'

    @property
    def ask_data_url(self):
        return f'https://algospace.top/algo/{self.lower_name}/service/ask_data'

    @property
    def return_ans_url(self):
        return f'https://algospace.top/algo/{self.lower_name}/service/return_ans'

    @property
    def return_err_url(self):
        return f'https://algospace.top/algo/{self.lower_name}/service/error_ans'

    @property
    def gradio_upload_url(self):
        return f'https://algospace.top/algo/{self.lower_name}/gradio_worker/upload'

    @property
    def storage_file_url(self):
        return 'https://algospace.top/core/storage/file'

    @property
    def gradio_page(self):
        return f'https://algospace.top/algo/{self.lower_name}/gradio/'

    @property
    def algorithm_site(self):
        return f'https://algospace.top/algorithm/{self.name}/{self.version}'

    @property
    def get_service_status_url(self):
        return 'https://algospace.top/core/algo/builder/status'

    @property
    def upload_code_url(self):
        return f'https://algospace.top/core/algo/builder/file/{self.name}/{self.version}'

    @property
    def start_build_url(self):
        return 'https://algospace.top/core/algo/builder/start'

    @property
    def reset_status_url(self):
        return 'https://algospace.top/core/algo/builder/reset'

    @property
    def get_build_ws_url(self):
        return 'wss://algospace.top/core/algo/builder/ws/log'

    @property
    def start_deploy_url(self):
        return 'https://algospace.top/core/algo/dispatcher/start'

    @property
    def get_deploy_ws_url(self):
        return 'wss://algospace.top/core/algo/dispatcher/ws/log'
