#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 配置加载器
@Author: Kermit
@Date: 2022-11-05 20:19:06
@LastEditors: Kermit
@LastEditTime: 2023-03-29 17:34:23
'''

import os
import sys
import re
from typing import Callable, Optional, Union
from algospace.exceptions import ConfigError


class ParamType:
    STRING = 'str'
    INTEGER = 'int'
    FLOAT = 'float'
    IMAGE_PATH = 'image_path'
    VIDEO_PATH = 'video_path'
    VOICE_PATH = 'voice_path'


class InputType(ParamType):
    @classmethod
    def String(cls, describe: str = '', max_length: Optional[int] = None, default: Optional[str] = None) -> dict:
        ''' 字符串 '''
        return {
            'type': cls.STRING,
            'describe': describe,
            **({'max_length': max_length} if max_length is not None else {}),
            **({'default': default} if default is not None else {}),
        }

    @classmethod
    def Integer(cls, describe: str = '', min_value: Optional[int] = None, max_value: Optional[int] = None, default: Optional[int] = None) -> dict:
        ''' 定点数 '''
        return {
            'type': cls.INTEGER,
            'describe': describe,
            **({'min_value': min_value} if min_value is not None else {}),
            **({'max_value': max_value} if max_value is not None else {}),
            **({'default': default} if default is not None else {}),
        }

    @classmethod
    def Float(cls, describe: str = '', min_value: Optional[int] = None, max_value: Optional[int] = None, max_fraction: Optional[int] = None, default: Optional[float] = None) -> dict:
        ''' 浮点数 '''
        return {
            'type': cls.FLOAT,
            'describe': describe,
            **({'min_value': min_value} if min_value is not None else {}),
            **({'max_value': max_value} if max_value is not None else {}),
            **({'max_fraction': max_fraction} if max_fraction is not None else {}),
            **({'default': default} if default is not None else {}),
        }

    @classmethod
    def ImagePath(cls, describe: str = '', max_size: Optional[Union[float, int]] = None, default: Optional[str] = None) -> dict:
        ''' 图片路径 '''
        return {
            'type': cls.IMAGE_PATH,
            'describe': describe,
            **({'max_size': max_size} if max_size is not None else {}),
            **({'default': default} if default is not None else {}),
        }

    @classmethod
    def VideoPath(cls, describe: str = '', max_size: Optional[Union[float, int]] = None, default: Optional[str] = None) -> dict:
        ''' 视频路径 '''
        return {
            'type': cls.VIDEO_PATH,
            'describe': describe,
            **({'max_size': max_size} if max_size is not None else {}),
            **({'default': default} if default is not None else {}),
        }

    @classmethod
    def VoicePath(cls, describe: str = '', max_size: Optional[Union[float, int]] = None, default: Optional[str] = None) -> dict:
        ''' 音频路径 '''
        return {
            'type': cls.VOICE_PATH,
            'describe': describe,
            **({'max_size': max_size} if max_size is not None else {}),
            **({'default': default} if default is not None else {}),
        }


class OutputType(ParamType):
    @classmethod
    def String(cls, describe: str = '') -> dict:
        ''' 字符串 '''
        return {
            'type': cls.STRING,
            'describe': describe,
        }

    @classmethod
    def Integer(cls, describe: str = '') -> dict:
        ''' 定点数 '''
        return {
            'type': cls.INTEGER,
            'describe': describe,
        }

    @classmethod
    def Float(cls, describe: str = '') -> dict:
        ''' 浮点数 '''
        return {
            'type': cls.FLOAT,
            'describe': describe,
        }

    @classmethod
    def ImagePath(cls, describe: str = '') -> dict:
        ''' 图片路径 '''
        return {
            'type': cls.IMAGE_PATH,
            'describe': describe,
        }

    @classmethod
    def VideoPath(cls, describe: str = '') -> dict:
        ''' 视频路径 '''
        return {
            'type': cls.VIDEO_PATH,
            'describe': describe,
        }

    @classmethod
    def VoicePath(cls, describe: str = '') -> dict:
        ''' 音频路径 '''
        return {
            'type': cls.VOICE_PATH,
            'describe': describe,
        }


valid_input_type = [getattr(InputType, x) for x in dir(InputType) if not x.startswith('__')]
valid_output_type = [getattr(OutputType, x) for x in dir(OutputType) if not x.startswith('__')]


class ConfigLoader:
    def __init__(self, config_path: str, is_verify_service: bool = False, is_verify_self_gradio_launch: bool = False) -> None:
        self.config_path = config_path
        self.is_verify_service = is_verify_service
        self.is_verify_self_gradio_launch = is_verify_self_gradio_launch
        # 导入配置
        config_dirpath = os.path.split(config_path)[0]
        config_filename = os.path.split(config_path)[1]
        config_filename_noext = os.path.splitext(config_filename)[0]
        sys.path.insert(0, config_dirpath)
        config = __import__(config_filename_noext)
        sys.path.pop(0)
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config_file_content = f.read()
            self.config_dirpath = config_dirpath

        self.name: str = getattr(config, 'name', '')
        self.version: str = getattr(config, 'version', '')
        self.secret: str = getattr(config, 'secret', '')
        self.username: str = getattr(config, 'username', '')
        self.password: str = getattr(config, 'password', '')
        self.service_filepath: str = getattr(config, 'service_filepath', '')
        self.service_function: str = getattr(config, 'service_function', '')
        self.service_input: dict = getattr(config, 'service_input')
        self.service_output: dict = getattr(config, 'service_output')
        self.service_input_examples: list[dict] = getattr(config, 'service_input_examples', [])
        self.service_max_parallel: int = int(getattr(config, 'service_max_parallel', 1))
        self.service_timeout: float = float(getattr(config, 'service_timeout', 60))
        self.service_tmp_dir: str = getattr(config, 'service_tmp_dir', '/tmp')

        self.description: str = getattr(config, 'description', '')
        self.scope: str = getattr(config, 'scope', 'PRIVATE')
        self.chinese_name: str = getattr(config, 'chinese_name', '')
        self.document_filepath: str = getattr(config, 'document_filepath', '')
        self.document: str = ''

        self.requirements: list[str] = getattr(config, 'requirements', [])
        self.pre_command: list[str] = getattr(config, 'pre_command', [])
        self.base_image: str = getattr(config, 'base_image', 'python:3.9')

        self.gradio_launch_filepath: str = getattr(config, 'gradio_launch_filepath', '')
        self.gradio_launch_function: str = getattr(config, 'gradio_launch_function', '')
        self.gradio_launch_host: str = getattr(config, 'gradio_launch_host', '127.0.0.1')
        self.gradio_launch_port: int = getattr(config, 'gradio_launch_port', 7860)
        self.is_self_gradio_launch = bool(self.gradio_launch_filepath and self.gradio_launch_function)

        if self.is_self_gradio_launch:
            self.gradio_server_host = self.gradio_launch_host
            self.gradio_server_port = self.gradio_launch_port
        else:
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

        if type(self.secret) != str:
            raise ConfigError('ConfigError: \'secret\' is not str.')
        if type(self.username) != str:
            raise ConfigError('ConfigError: \'username\' is not str.')
        if type(self.password) != str:
            raise ConfigError('ConfigError: \'password\' is not str.')
        if len(self.secret) == 0 and (len(self.password) == 0 or len(self.username) == 0):
            raise ConfigError('ConfigError: \'secret\' or \'password\' is empty.')

        if type(self.service_filepath) != str:
            raise ConfigError('ConfigError: \'service_filepath\' is not str.')
        if len(self.service_filepath) == 0:
            raise ConfigError('ConfigError: \'service_filepath\' is empty.')
        if not os.path.exists(self._get_service_file_info()['service_filepath']):
            raise ConfigError(f'ConfigError: file \'{self.service_filepath}\' does not exist.')

        if type(self.service_function) != str:
            raise ConfigError('ConfigError: \'service_function\' is not str.')
        if len(self.service_function) == 0:
            raise ConfigError('ConfigError: \'service_function\' is empty.')
        if self.is_verify_service:
            self.verify_service()

        if type(self.service_input) != dict:
            raise ConfigError('ConfigError: \'service_input\' is not dict.')
        if len(self.service_input) == 0:
            raise ConfigError('ConfigError: \'service_input\' is empty.')
        for key, info in self.service_input.items():
            if type(key) != str:
                raise ConfigError(f'ConfigError: key \'{str(key)}\' in \'service_input\' is not str.')
            if type(info) != dict:
                raise ConfigError(f'ConfigError: value of \'{str(key)}\' in \'service_input\' is not dict.')
            if info.get('type', '') not in valid_input_type:
                raise ConfigError(
                    f'ConfigError: type of \'{str(key)}\' in \'service_input\' is not in {str(valid_input_type)}.')
            info['describe'] = str(info.get('describe', ''))
            if info.get('max_length', None) is not None and info['type'] != InputType.STRING:
                raise ConfigError(f'ConfigError: max_length of \'{str(key)}\' in \'service_input\' is not allowed.')
            if info.get('max_length', None) is not None and type(info['max_length']) != int:
                raise ConfigError(f'ConfigError: max_length of \'{str(key)}\' in \'service_input\' is not int.')
            if info.get('min_value', None) is not None and info['type'] not in [InputType.INTEGER, InputType.FLOAT]:
                raise ConfigError(f'ConfigError: min_value of \'{str(key)}\' in \'service_input\' is not allowed.')
            if info.get('min_value', None) is not None and type(info['min_value']) not in [int, float]:
                raise ConfigError(f'ConfigError: min_value of \'{str(key)}\' in \'service_input\' is not int or float.')
            if info.get('max_value', None) is not None and info['type'] not in [InputType.INTEGER, InputType.FLOAT]:
                raise ConfigError(f'ConfigError: max_value of \'{str(key)}\' in \'service_input\' is not allowed.')
            if info.get('max_value', None) is not None and type(info['max_value']) not in [int, float]:
                raise ConfigError(f'ConfigError: max_value of \'{str(key)}\' in \'service_input\' is not int or float.')
            if info.get('min_value', None) is not None and info.get('max_value', None) is not None and \
                    info['min_value'] > info['max_value']:
                raise ConfigError(
                    f'ConfigError: min_value of \'{str(key)}\' in \'service_input\' is greater than max_value.')
            if info.get('max_fraction', None) is not None and info['type'] != InputType.FLOAT:
                raise ConfigError(f'ConfigError: max_fraction of \'{str(key)}\' in \'service_input\' is not allowed.')
            if info.get('max_fraction', None) is not None and type(info['max_fraction']) != int:
                raise ConfigError(f'ConfigError: max_fraction of \'{str(key)}\' in \'service_input\' is not int.')
            if info.get('max_size', None) is not None and info['type'] not in [InputType.IMAGE_PATH, InputType.VIDEO_PATH, InputType.VOICE_PATH]:
                raise ConfigError(f'ConfigError: max_size of \'{str(key)}\' in \'service_input\' is not allowed.')
            if info.get('max_size', None) is not None and type(info['max_size']) not in [int, float]:
                raise ConfigError(f'ConfigError: max_size of \'{str(key)}\' in \'service_input\' is not int or float.')
            if info.get('default', None) is not None and info['type'] in [InputType.STRING, InputType.IMAGE_PATH, InputType.VIDEO_PATH, InputType.VOICE_PATH] and type(info['default']) != str:
                raise ConfigError(f'ConfigError: default of \'{str(key)}\' in \'service_input\' is not str.')
            if info.get('default', None) is not None and info['type'] in [InputType.INTEGER, InputType.FLOAT] and type(info['default']) not in [int, float]:
                raise ConfigError(f'ConfigError: default of \'{str(key)}\' in \'service_input\' is not int or float.')
            if info.get('default', None) is not None and info['type'] in [InputType.IMAGE_PATH, InputType.VIDEO_PATH, InputType.VOICE_PATH]:
                info['default'] = os.path.join(self.config_dirpath, info['default'])
                if not os.path.exists(info['default']):
                    raise ConfigError(f'ConfigError: default of \'{str(key)}\' in \'service_input\' does not exist.')

        if type(self.service_output) != dict:
            raise ConfigError('ConfigError: \'service_output\' is not dict.')
        if len(self.service_output) == 0:
            raise ConfigError('ConfigError: \'service_output\' is empty.')
        for key, info in self.service_output.items():
            if type(key) != str:
                raise ConfigError(f'ConfigError: key \'{str(key)}\' in \'service_output\' is not str.')
            if type(info) != dict:
                raise ConfigError(f'ConfigError: value of \'{str(key)}\' in \'service_output\' is not dict.')
            if info.get('type', '') not in valid_output_type:
                raise ConfigError(
                    f'ConfigError: type of \'{str(key)}\' in \'service_output\' is not in {str(valid_output_type)}.')
            info['describe'] = str(info.get('describe', ''))

        if type(self.service_input_examples) != list:
            raise ConfigError('ConfigError: \'service_input_examples\' is not list.')
        for index, input_example in enumerate(self.service_input_examples):
            if type(input_example) != dict:
                raise ConfigError('ConfigError: \'service_input_examples\' contains not dict.')
            if len(input_example) != len(self.service_input):
                raise ConfigError(
                    f'ConfigError: item {index} in \'service_input_examples\' does not match \'service_input\'.')
            for key, value in input_example.items():
                if key not in self.service_input:
                    raise ConfigError(
                        f'ConfigError: key \'{str(key)}\' in \'service_input_examples\' is not in \'service_input\'.')
                if self.service_input[key]['type'] in [InputType.IMAGE_PATH, InputType.VIDEO_PATH, InputType.VOICE_PATH]:
                    if type(value) != str:
                        raise ConfigError(
                            f'ConfigError: value of \'{str(key)}\' in \'service_input_examples\' is not str.')
                    input_example[key] = os.path.join(self.config_dirpath, value)
                    if not os.path.exists(input_example[key]):
                        raise ConfigError(
                            f'ConfigError: value of \'{str(key)}\' in \'service_input_examples\' does not exist.')
                elif self.service_input[key]['type'] == InputType.STRING:
                    if type(value) != str:
                        raise ConfigError(
                            f'ConfigError: value of \'{str(key)}\' in \'service_input_examples\' is not str.')
                elif self.service_input[key]['type'] == InputType.INTEGER:
                    if type(value) != int:
                        raise ConfigError(
                            f'ConfigError: value of \'{str(key)}\' in \'service_input_examples\' is not int.')
                elif self.service_input[key]['type'] == InputType.FLOAT:
                    if type(value) not in [int, float]:
                        raise ConfigError(
                            f'ConfigError: value of \'{str(key)}\' in \'service_input_examples\' is not int or float.')

        if type(self.service_max_parallel) != int:
            raise ConfigError('ConfigError: \'service_max_parallel\' is not int.')
        if self.service_max_parallel <= 0:
            raise ConfigError('ConfigError: \'service_max_parallel\' is less than 0.')

        if type(self.service_timeout) != float:
            raise ConfigError('ConfigError: \'service_timeout\' is not float.')
        if self.service_timeout <= 0:
            raise ConfigError('ConfigError: \'service_timeout\' is less than 0.')

        if type(self.service_tmp_dir) != str:
            raise ConfigError('ConfigError: \'service_tmp_dir\' is not str.')

        if type(self.description) != str:
            raise ConfigError('ConfigError: \'description\' is not str.')
        if type(self.scope) != str:
            raise ConfigError('ConfigError: \'scope\' is not str.')
        if self.scope not in ['PRIVATE', 'GROUP', 'INSTITUTION', 'PUBLIC']:
            raise ConfigError('ConfigError: \'scope\' is not in \'PRIVATE\',\'GROUP\',\'INSTITUTION\',\'PUBLIC\'.')
        if type(self.chinese_name) != str:
            raise ConfigError('ConfigError: \'chinese_name\' is not str.')
        if type(self.document_filepath) != str:
            raise ConfigError('ConfigError: \'document_filepath\' is not str.')
        if self.document_filepath and not self._read_document_file():
            raise ConfigError(f'ConfigError: \'{self.document_filepath}\' does not exist.')

        if type(self.requirements) != list:
            raise ConfigError('ConfigError: \'requirements\' is not list.')
        for requirements_item in self.requirements:
            if type(requirements_item) != str:
                raise ConfigError('ConfigError: Item in \'requirements\' is not str.')

        if type(self.pre_command) != list:
            raise ConfigError('ConfigError: \'pre_command\' is not list.')
        for pre_command_item in self.pre_command:
            if type(pre_command_item) != str:
                raise ConfigError('ConfigError: Item in \'pre_command\' is not str.')
        if type(self.base_image) != str:
            raise ConfigError('ConfigError: \'base_image\' is not str.')

        if self.is_self_gradio_launch:
            if type(self.gradio_launch_filepath) != str:
                raise ConfigError('ConfigError: \'gradio_launch_filepath\' is not str.')
            if not os.path.exists(self._get_gradio_launch_file_info()['gradio_launch_filepath']):
                raise ConfigError(f'ConfigError: file \'{self.gradio_launch_filepath}\' does not exist.')
            if type(self.gradio_launch_function) != str:
                raise ConfigError('ConfigError: \'gradio_launch_function\' is not str.')
            if self.is_verify_self_gradio_launch:
                self.verify_gradio_launch()

            if type(self.gradio_launch_host) != str:
                raise ConfigError('ConfigError: \'gradio_launch_host\' is not str.')
            if len(self.gradio_launch_host) == 0:
                raise ConfigError('ConfigError: \'gradio_launch_host\' is empty.')
            if type(self.gradio_launch_port) != int:
                raise ConfigError('ConfigError: \'gradio_launch_port\' is not int.')

    @property
    def fn(self) -> Callable:
        return self._get_service_fn()  # type: ignore

    def verify_service(self) -> None:
        if self._import_service_file() is None:
            raise ConfigError(
                f'ConfigError: \'{self.service_function}\' does not exist.')
        if not hasattr(self._get_service_fn(), '__call__'):
            raise ConfigError(
                f'ConfigError: \'{self.service_function}\' is not callable.')

    def _get_service_fn(self) -> Optional[Callable]:
        return getattr(self._import_service_file(), self.service_function, None)

    def _import_service_file(self):
        service_path = self._get_service_file_info()['service_path']
        service_filename_noext = self._get_service_file_info()['service_filename_noext']
        if service_path not in sys.path:
            sys.path.insert(0, service_path)
        return __import__(service_filename_noext)

    def _get_service_file_info(self) -> dict:
        service_path = os.path.join(self.config_dirpath, os.path.split(self.service_filepath)[0])
        service_filename = os.path.split(self.service_filepath)[1]
        service_filename_noext = os.path.splitext(service_filename)[0]
        service_filepath = os.path.join(service_path, service_filename)
        return {
            'service_path': service_path,
            'service_filename': service_filename,
            'service_filename_noext': service_filename_noext,
            'service_filepath': service_filepath,
        }

    @property
    def service_tmp_path(self) -> str:
        return os.path.join(self.config_dirpath, self.service_tmp_dir)

    def _is_document_file_exist(self) -> bool:
        document_filepath = os.path.join(self.config_dirpath, self.document_filepath)
        return os.path.exists(document_filepath)

    def _read_document_file(self) -> bool:
        if not self._is_document_file_exist():
            return False
        document_filepath = os.path.join(self.config_dirpath, self.document_filepath)
        with open(document_filepath, 'r', encoding='utf-8') as f:
            self.document = f.read()
        return True

    @property
    def gradio_launch_fn(self) -> Callable:
        return self._get_gradio_launch_fn()  # type: ignore

    def verify_gradio_launch(self) -> None:
        if self._import_gradio_launch_file() is None:
            raise ConfigError(
                f'ConfigError: \'{self.gradio_launch_function}\' does not exist.')
        if not hasattr(self._get_gradio_launch_fn(), '__call__'):
            raise ConfigError(
                f'ConfigError: \'{self.gradio_launch_function}\' is not callable.')

    def _get_gradio_launch_fn(self) -> Optional[Callable]:
        return getattr(self._import_gradio_launch_file(), self.gradio_launch_function, None)

    def _import_gradio_launch_file(self):
        gradio_launch_path = self._get_gradio_launch_file_info()['gradio_launch_path']
        gradio_launch_filename_noext = self._get_gradio_launch_file_info()['gradio_launch_filename_noext']
        if gradio_launch_path not in sys.path:
            sys.path.insert(0, gradio_launch_path)
        return __import__(gradio_launch_filename_noext)

    def _get_gradio_launch_file_info(self) -> dict:
        gradio_launch_path = os.path.join(self.config_dirpath, os.path.split(self.gradio_launch_filepath)[0])
        gradio_launch_filename = os.path.split(self.gradio_launch_filepath)[1]
        gradio_launch_filename_noext = os.path.splitext(gradio_launch_filename)[0]
        gradio_launch_filepath = os.path.join(gradio_launch_path, gradio_launch_filename)
        return {
            'gradio_launch_path': gradio_launch_path,
            'gradio_launch_filename': gradio_launch_filename,
            'gradio_launch_filename_noext': gradio_launch_filename_noext,
            'gradio_launch_filepath': gradio_launch_filepath,
        }
