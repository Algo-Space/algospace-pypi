#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 配置生成器
@Author: Kermit
@Date: 2022-11-07 17:30:04
@LastEditors: Kermit
@LastEditTime: 2023-02-03 17:09:19
'''

import os
import traceback
from algospace.logger import algospace_logger_notime


def generate_config():
    try:
        if os.path.exists('algospace-config.py'):
            algospace_logger_notime.warning('Init Error: \'algospace-config.py\' exists.')
            return
        with open(os.path.join(os.path.split(__file__)[0], 'templates', 'algospace-config.py'), 'r', encoding='utf-8') as f:
            template = f.read()
        with open('algospace-config.py', 'w') as f:
            f.write(template)
        algospace_logger_notime.info('Init successfully!')
        print('-----------------------------')
        print('已在当前目录下生成 \'algospace-config.py\' 文件，填写算法信息后，即可通过 \'algospace start\' 命令一键启动。')
    except Exception as e:
        traceback.print_exc()
        algospace_logger_notime.error('Init Error: ' + str(e))
        exit(1)
