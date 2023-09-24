#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 日志
@Author: Kermit
@Date: 2023-02-03 16:29:34
@LastEditors: Kermit
@LastEditTime: 2023-09-24 16:47:32
'''


import time


class Logger:
    def __init__(self, scope: str, is_show_time: bool = True) -> None:
        self.scope = scope
        self.is_show_time = is_show_time

    def info(self, *msg: object) -> None:
        print(*([f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]']
              if self.is_show_time else []), f'[{self.scope}]', '[INFO]', *msg)

    def error(self, *msg: object) -> None:
        print(*([f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]']
              if self.is_show_time else []), f'[{self.scope}]', '[ERROR]', *msg)

    def debug(self, *msg: object) -> None:
        print(*([f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]']
              if self.is_show_time else []), f'[{self.scope}]', '[DEBUG]', *msg)

    def warning(self, *msg: object) -> None:
        print(*([f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]']
              if self.is_show_time else []), f'[{self.scope}]', '[WARNING]', *msg)


algospace_logger = Logger('AlgoSpace', is_show_time=True)
algospace_logger_notime = Logger('AlgoSpace', is_show_time=False)
