#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 算法函数类
@Author: Kermit
@Date: 2022-11-11 15:47:20
@LastEditors: Kermit
@LastEditTime: 2023-02-03 21:04:23
'''

from typing import Optional, Callable
from algospace.login import login_instance
import os
import re
import requests
from . import config
from algospace.exceptions import CallException, TimeOutException
from algospace.provider.config_loader import InputType, OutputType, valid_input_type, valid_output_type
import base64


class AlgoFunction:
    ''' 算法函数 '''

    def __init__(self, name: str, version: Optional[str] = None, timeout: int = config.call_timeout) -> None:
        self.name = name
        self.version = version
        self.timeout = timeout
        self.info = None
        pass

    def convert_file_dict(self, local_path: str) -> dict:
        ''' 将本地 path 转换为 file 字典 '''
        if local_path.startswith('http'):
            format = re.sub(r'\?.*$', '', os.path.splitext(local_path)[-1].replace('.', ''))
            return {
                'type': 'url',
                'data': local_path,
                'format': format,
            }
        else:
            format = os.path.splitext(local_path)[-1].replace('.', '')
            with open(local_path, 'rb') as f:
                base64_data = base64.b64encode(f.read())
            return {
                'type': 'base64',
                'data': base64_data.decode(),
                'format': format,
            }

    def convert_url(self, path: str) -> str:
        ''' 将 path 转换为 url '''
        upload_url = f'{config.storage_file_url}/{path}'
        return upload_url

    def get_input_type_class(self, input_type: str) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if input_type not in valid_input_type:
            raise Exception(
                f'Input type \'{input_type}\' is not available. Please try to update your algospace version.')
        elif input_type == InputType.STRING:
            return str
        elif input_type == InputType.INTEGER:
            return int
        elif input_type == InputType.FLOAT:
            return float
        elif input_type == InputType.IMAGE_PATH:
            return self.convert_file_dict
        elif input_type == InputType.VIDEO_PATH:
            return self.convert_file_dict
        elif input_type == InputType.VOICE_PATH:
            return self.convert_file_dict
        else:
            return str

    def get_output_type_class(self, output_type: str) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if output_type not in valid_output_type:
            raise Exception(
                f'Output type \'{output_type}\' is not available. Please try to update your algospace version.')
        elif output_type == OutputType.STRING:
            return str
        elif output_type == OutputType.INTEGER:
            return int
        elif output_type == OutputType.FLOAT:
            return float
        elif output_type == OutputType.IMAGE_PATH:
            return self.convert_url
        elif output_type == OutputType.VIDEO_PATH:
            return self.convert_url
        elif output_type == OutputType.VOICE_PATH:
            return self.convert_url
        else:
            return str

    def __call__(self, *args: list, **kwds: dict) -> dict:
        ''' 调用函数 '''
        info = self.get_info()
        can_call = info['can_call']
        input_param = info['input_param']
        output_param = info['output_param']
        if not can_call:
            raise Exception('This algorithm is not callable now because the provider closed the service.')

        kwargs = {}
        for index, arg in enumerate(args):
            if len(input_param) == index:
                break
            kwargs[input_param[index]['key']] = arg
        kwargs.update(kwds)
        for param in input_param:
            if param['key'] not in kwargs.keys():
                self.show_example()
                raise Exception('Arguments are not correct. Please refer to the example above.')
            param_key = param['key']
            param_type = param['type']
            kwargs[param_key] = self.get_input_type_class(param_type)(kwargs[param_key])

        try:
            response = requests.post(info['predict_url'],
                                     json=kwargs,
                                     headers=login_instance.get_header(),
                                     timeout=self.timeout)
        except requests.exceptions.ReadTimeout:
            raise TimeOutException('Call algorithm function timeout.')
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(response.status_code, response.content.decode())
        if response.json()['status'] != 200:
            raise CallException(response.json().get('err_msg', 'Call algorithm function error.'))

        result_status = response.json()['data']['status']
        result = response.json()['data']['result']
        if result_status == 'error':
            raise CallException(
                f'There is something wrong in algorithm provider service: {result.get("err_msg", "(no error message).")}')

        for param in output_param:
            param_key = param['key']
            param_type = param['type']
            result[param_key] = self.get_output_type_class(param_type)(result[param_key])
        return result

    def get_info(self) -> dict:
        ''' 获取算法信息 '''
        if not self.info:
            query_dict = {'name': self.name}
            if self.version:
                query_dict['version'] = self.version
            response = requests.get(config.algo_info_url, params=query_dict, headers=login_instance.get_header())
            if response.status_code != 200 and response.status_code != 201 and response.json()['status'] != 200:
                raise Exception('Failed to get info.')
            algo_list = response.json()['data']['list']
            if len(algo_list) == 0:
                raise Exception(f'No algorithm named {self.name + (" " + self.version if self.version else "")}.')
            algo = algo_list[0]
            self.info = {
                'name': algo['name'],
                'version': algo['version'],
                'can_call': algo['can_call'],
                'input_param': algo['input_param'],
                'output_param': algo['output_param'],
                'create_date': algo['create_date'],
                'example': algo['example'],
                'output_example': algo['output_example'],
                'predict_url': algo['predict_url'],
                'get_result_url': algo['get_result_url']
            }
        return self.info

    def show_example(self):
        ''' 展示示例 '''
        info = self.get_info()
        print('调用方式:')
        print(info['example'])
        print('')
        print('返回示例:')
        print(info['output_example'])
        print('')
