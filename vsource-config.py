#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-11-05 17:49:11
@LastEditors: Kermit
@LastEditTime: 2022-12-01 18:23:44
'''


###########
# 必填选项 #
###########

name = 'ckm_test'  # 算法名：仅能包含英文字母、数字和 _ - @ 符号
version = 'v1.0'  # 算法版本：仅能包含英文字母、数字和 . 符号

username = 'ckm'  # 登录名
password = 'ckmDBIIR'  # 密码

service_filepath = 'main.py'  # 服务文件
service_function = 'convert_text'  # 服务函数
service_input = {
    'txt': {
        'type': 'str',
        'describe': 'your text',
    }
}  # 输入参数
service_output = {
    'output_text': {
        'type': 'str',
        'describe': 'converted text'
    }
}  # 输出参数，输出需为字典

###########
# 可选选项 #
###########

description = '这是算法描述'

###################
# 容器内运行必填选项 #
###################

# 依赖包
requirements = [
    'pillow',
    'numpy',
    'requests',
    'opencv-python',
    'yacs',
    'matplotlib',
    'scipy',
    'envs/torch-1.9.0+cpu-cp36-cp36m-linux_x86_64.whl',
]
# 开始前指令
pre_command = [
    'apt install -y libgl1-mesa-glx',
]
