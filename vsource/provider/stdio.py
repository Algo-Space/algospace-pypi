#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 标准输入输出处理
@Author: Kermit
@Date: 2022-11-07 14:56:36
@LastEditors: Kermit
@LastEditTime: 2022-11-07 16:47:12
'''

import sys
import os
from typing import Callable
import time


class RedirectPrint:
    ''' 重定向标准输出 '''

    def __init__(self, write: Callable):
        self.write = write
        self.original_stdout_write = None

    def open(self):
        sys.stdout.close()
        sys.stdout.write = self.original_stdout_write  # type: ignore

    def close(self):
        self.original_stdout_write = sys.stdout.write
        sys.stdout.write = self.write  # type: ignore

    def __enter__(self):
        self.close()

    def __exit__(self):
        self.open()


class HiddenPrint:
    ''' 隐藏标准输出 '''

    def __init__(self):
        self.original_stdout = None

    def open(self):
        sys.stdout.close()
        sys.stdout = self.original_stdout

    def close(self):
        self.original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __enter__(self):
        self.close()

    def __exit__(self):
        self.open()


class GradioPrint(RedirectPrint):
    ''' 用以 Gradio Service 的标准输出 '''

    def __init__(self):
        def write(arg):
            if arg != '\n' and arg != '\r':
                self.original_stdout_write(
                    f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] [Gradio Service] {str(arg)}')  # type: ignore
            else:
                self.original_stdout_write(arg)  # type: ignore

        super().__init__(write)
