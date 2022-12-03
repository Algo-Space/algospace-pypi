#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-24 14:45:40
@LastEditors: Kermit
@LastEditTime: 2022-12-03 20:31:23
'''

import os


call_interval = 1
sleep_interval = 7


enroll_url = 'https://vsource.club/core/algo/pypi/enroll'
verify_config_url = 'https://vsource.club/core/algo/pypi/verify'
is_component_normal_url = 'https://vsource.club/core/algo/pypi/is_component_normal'


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
    def heartbeat_url(self):
        return 'https://vsource.club/core/heartbeat/send'

    @property
    def ask_data_url(self):
        return f'https://vsource.club/algo/{self.lower_name}/service/ask_data'

    @property
    def return_ans_url(self):
        return f'https://vsource.club/algo/{self.lower_name}/service/return_ans'

    @property
    def return_err_url(self):
        return f'https://vsource.club/algo/{self.lower_name}/service/error_ans'

    @property
    def gradio_upload_url(self):
        return f'https://vsource.club/algo/{self.lower_name}/gradio_worker/upload'

    @property
    def storage_file_url(self):
        return 'https://vsource.club/core/storage/file'

    @property
    def gradio_page(self):
        return f'https://vsource.club/algo/{self.lower_name}/gradio/'
    
    @property
    def algorithm_site(self):
        return f'https://vsource.club/algorithm/{self.name}/{self.version}'
