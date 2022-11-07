#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 配置生成器
@Author: Kermit
@Date: 2022-11-07 17:30:04
@LastEditors: Kermit
@LastEditTime: 2022-11-07 17:39:32
'''

import os


def generate_config():
    if os.path.exists('vsource_config.py'):
        print('[Vsource] Init Error: \'vsource_config.py\' exists.')
        return
    with open(os.path.join(os.path.split(__file__)[0], 'config_template.py'), 'r') as f:
        template = f.read()
    with open('vsource_config.py', 'w') as f:
        f.write(template)
    print('[Vsource] Init successfully! ')
    print('-----------------------------')
    print('已在当前目录下生成 \'vsource_config.py\' 文件，填写算法信息后，即可通过 \'vsource start\' 命令一键启动。')
