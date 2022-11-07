#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 配置加载器
@Author: Kermit
@Date: 2022-11-05 20:19:06
@LastEditors: Kermit
@LastEditTime: 2022-11-07 16:27:54
'''

import os
import sys
import re
from typing import Callable, Optional
from vsource.exceptions import ConfigError

valid_param_type = ['str', 'int', 'float', 'image_path', 'video_path', 'voice_path']


class ConfigLoader:
    def __init__(self, config_path: str) -> None:
        config_dirpath = os.path.split(config_path)[0]
        config_filename = os.path.split(config_path)[1]
        config_filename_noext = os.path.splitext(config_filename)[0]
        sys.path.insert(0, config_dirpath)
        config = __import__(config_filename_noext)
        sys.path.pop(0)

        self.name: str = getattr(config, 'name', '')
        self.version: str = getattr(config, 'version', '')
        self.username: str = getattr(config, 'username', '')
        self.password: str = getattr(config, 'password', '')
        self.service_filepath: str = getattr(config, 'service_filepath', '')
        self.service_function: str = getattr(config, 'service_function', '')
        self.service_input: dict = getattr(config, 'service_input')
        self.service_output: dict = getattr(config, 'service_output')

        self.description: str = getattr(config, 'description', '')
        self.gradio_server_host = '127.0.0.1'
        self.gradio_server_port = 7860

        self._verify()

    def _verify(self) -> None:
        if type(self.name) != str:
            raise ConfigError('ConfigError: \'name\' is not str.')
        if len(self.name) == 0:
            raise ConfigError('ConfigError: \'name\' is empty.')
        if not bool(re.match('^[a-zA-Z0-9_\-@]+$', self.name)):
            raise ConfigError('ConfigError: \'name\' can only include \'a-z A-Z 0-9 _ - @\'.')

        if type(self.version) != str:
            raise ConfigError('ConfigError: \'version\' is not str.')
        if len(self.version) == 0:
            raise ConfigError('ConfigError: \'version\' is empty.')
        if not bool(re.match('^[a-zA-Z0-9\.]+$', self.version)):
            raise ConfigError('ConfigError: \'version\' can only include \'a-z A-Z 0-9 .\'.')

        if type(self.username) != str:
            raise ConfigError('ConfigError: \'username\' is not str.')
        if len(self.username) == 0:
            raise ConfigError('ConfigError: \'username\' is empty.')

        if type(self.password) != str:
            raise ConfigError('ConfigError: \'password\' is not str.')
        if len(self.password) == 0:
            raise ConfigError('ConfigError: \'password\' is empty.')

        if type(self.service_filepath) != str:
            raise ConfigError('ConfigError: \'service_filepath\' is not str.')
        if len(self.service_filepath) == 0:
            raise ConfigError('ConfigError: \'service_filepath\' is empty.')
        if not os.path.exists(self.service_filepath):
            raise ConfigError(
                f'ConfigError: file \'{self.service_filepath}\' does not exist.')

        if type(self.service_function) != str:
            raise ConfigError('ConfigError: \'service_function\' is not str.')
        if len(self.service_function) == 0:
            raise ConfigError('ConfigError: \'service_function\' is empty.')
        if self._import_service_file() is None:
            raise ConfigError(
                f'ConfigError: \'{self.service_function}\' does not exist.')
        if not hasattr(self._get_service_fn(), '__call__'):
            raise ConfigError(
                f'ConfigError: \'{self.service_function}\' is not callable.')

        if type(self.service_input) != dict:
            raise ConfigError('ConfigError: \'service_input\' is not dict.')
        if len(self.service_input) == 0:
            raise ConfigError('ConfigError: \'service_input\' is empty.')
        for key, info in self.service_input.items():
            if type(key) != str:
                raise ConfigError(f'ConfigError: key \'{str(key)}\' in \'service_input\' is not str.')
            if type(info) != dict:
                raise ConfigError(f'ConfigError: value of \'{str(key)}\' in \'service_input\' is not dict.')
            if info.get('type', '') not in valid_param_type:
                raise ConfigError(
                    f'ConfigError: type of \'{str(key)}\' in \'service_input\' is not in {str(valid_param_type)}.')
            info['describe'] = str(info.get('describe', ''))

        if type(self.service_output) != dict:
            raise ConfigError('ConfigError: \'service_output\' is not dict.')
        if len(self.service_output) == 0:
            raise ConfigError('ConfigError: \'service_output\' is empty.')
        for key, info in self.service_output.items():
            if type(key) != str:
                raise ConfigError(f'ConfigError: key \'{str(key)}\' in \'service_output\' is not str.')
            if type(info) != dict:
                raise ConfigError(f'ConfigError: value of \'{str(key)}\' in \'service_output\' is not dict.')
            if info.get('type', '') not in valid_param_type:
                raise ConfigError(
                    f'ConfigError: type of \'{str(key)}\' in \'service_output\' is not in {str(valid_param_type)}.')
            info['describe'] = str(info.get('describe', ''))

        if type(self.description) != str:
            raise ConfigError('ConfigError: \'description\' is not str.')

    @property
    def fn(self) -> Callable:
        return self._get_service_fn()  # type: ignore

    def _get_service_fn(self) -> Optional[Callable]:
        return getattr(self._import_service_file(), self.service_function, None)

    def _import_service_file(self):
        service_path = self._get_service_file_info()['service_path']
        service_filename_noext = self._get_service_file_info()['service_filename_noext']
        if service_path not in sys.path:
            sys.path.insert(0, service_path)
        return __import__(service_filename_noext)

    def _get_service_file_info(self) -> dict:
        service_path = os.path.split(self.service_filepath)[0]
        service_filename = os.path.split(self.service_filepath)[1]
        service_filename_noext = os.path.splitext(service_filename)[0]
        return {
            'service_path': service_path,
            'service_filename': service_filename,
            'service_filename_noext': service_filename_noext
        }
