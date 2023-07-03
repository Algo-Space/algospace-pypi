#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2023-05-22 16:50:32
@LastEditors: Kermit
@LastEditTime: 2023-05-22 17:33:54
'''

from typing import Tuple
from .config_loader import ConfigLoader, ParamType, valid_input_type
from . import config
import os


class ParamValidator:
    def __init__(self, algorithm_config: ConfigLoader):
        self.algorithm_config = algorithm_config

    def validate(self, *args, **kwargs) -> Tuple[bool, str]:
        ''' 检查输入参数是否符合限制条件 '''
        args_index = 0

        for key, info in self.algorithm_config.service_input.items():
            if args_index < len(args):
                result, err_msg = self.validate_input_param_restrict(info['type'], key, args[args_index], **info)
                if not result:
                    return False, err_msg
            else:
                if key not in kwargs:
                    return False, f'Input value \'{key}\' is not provided.'
                result, err_msg = self.validate_input_param_restrict(info['type'], key, kwargs[key], **info)
                if not result:
                    return False, err_msg

            args_index += 1

        return True, ''

    def validate_input_param_restrict(self, input_type: str, input_key: str, input_value, **restrict_dict) -> Tuple[bool, str]:
        ''' 单次检查输入参数是否符合限制条件 '''
        # 使用默认值
        if not restrict_dict.get('max_length'):
            restrict_dict['max_length'] = config.input_param_str_default_max_length
        if not restrict_dict.get('max_size'):
            if input_type == ParamType.IMAGE_PATH:
                restrict_dict['max_size'] = config.input_param_image_default_max_size
            elif input_type == ParamType.VIDEO_PATH:
                restrict_dict['max_size'] = config.input_param_video_default_max_size
            elif input_type == ParamType.VOICE_PATH:
                restrict_dict['max_size'] = config.input_param_voice_default_max_size

        # 检查输入参数是否符合限制条件
        if input_type not in valid_input_type:
            return False, f'Input type \'{input_type}\' is not available.'
        elif input_type == ParamType.STRING:
            if restrict_dict.get('max_length') is not None and len(input_value) > min(restrict_dict['max_length'], config.input_param_str_max_length):
                return False, f'Input value \'{input_key}\' is too long.'
        elif input_type == ParamType.INTEGER:
            if restrict_dict.get('min_value') is not None and input_value < restrict_dict['min_value']:
                return False, f'Input value \'{input_key}\' is too small.'
            if restrict_dict.get('max_value') is not None and input_value > restrict_dict['max_value']:
                return False, f'Input value \'{input_key}\' is too large.'
        elif input_type == ParamType.FLOAT:
            if restrict_dict.get('min_value') is not None and input_value < restrict_dict['min_value']:
                return False, f'Input value \'{input_key}\' is too small.'
            if restrict_dict.get('max_value') is not None and input_value > restrict_dict['max_value']:
                return False, f'Input value \'{input_key}\' is too large.'
            if restrict_dict.get('max_fraction') is not None and len(str(input_value).split('.')[1]) > restrict_dict['max_fraction']:
                return False, f'Input value \'{input_key}\' is too long.'
        elif input_type == ParamType.IMAGE_PATH:
            file_size = os.path.getsize(input_value) / (1024**2)
            if restrict_dict.get('max_size') is not None and \
                    file_size > min(restrict_dict['max_size'], config.input_param_image_max_size):
                return False, f'Input value \'{input_key}\' is too large.'
        elif input_type == ParamType.VIDEO_PATH:
            file_size = os.path.getsize(input_value) / (1024**2)
            if restrict_dict.get('max_size') is not None and \
                    file_size > min(restrict_dict['max_size'], config.input_param_video_max_size):
                return False, f'Input value \'{input_key}\' is too large.'
        elif input_type == ParamType.VOICE_PATH:
            file_size = os.path.getsize(input_value) / (1024**2)
            if restrict_dict.get('max_size') is not None and \
                    file_size > min(restrict_dict['max_size'], config.input_param_voice_max_size):
                return False, f'Input value \'{input_key}\' is too large.'
        else:
            return False, f'Input type \'{input_type}\' is not available.'

        return True, ''
