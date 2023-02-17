#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 工具
@Author: Kermit
@Date: 2023-02-03 16:18:13
@LastEditors: Kermit
@LastEditTime: 2023-02-03 16:18:54
'''

import time


def create_timestamp_filename() -> str:
    ''' 生成时间戳文件名 '''
    filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + \
        '-' + str(time.time() - int(time.time()))[2:10]  # '2023-02-03-16-15-37-85679793'
    return filename
