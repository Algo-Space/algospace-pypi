#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 配置生成器
@Author: Kermit
@Date: 2022-11-07 17:30:04
@LastEditors: Kermit
@LastEditTime: 2022-11-11 13:31:54
'''

import os
import traceback


def generate_config():
    try:
        if os.path.exists('vsource-config.py'):
            print('[Vsource] Init Error: \'vsource-config.py\' exists.')
            return
        with open(os.path.join(os.path.split(__file__)[0], 'templates', 'vsource-config.py'), 'r') as f:
            template = f.read()
        with open('vsource-config.py', 'w') as f:
            f.write(template)
        print('[Vsource] Init successfully!')
        print('-----------------------------')
        print('已在当前目录下生成 \'vsource-config.py\' 文件，填写算法信息后，即可通过 \'vsource start\' 命令一键启动。')
    except Exception as e:
        traceback.print_exc()
        print('[Vsource] Init error:', *e.args)
