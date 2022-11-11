#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: Vsource 包
@Author: DBIIR
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-11-11 19:57:03
'''

__version__ = 'v2.0.0'

from vsource.__main__ import run
from vsource.customer.service import login
from vsource.customer.service import info
from vsource.customer.service import fn
from vsource.customer.service import show_example
from vsource.customer.service import call
from vsource.customer.service import clear_storage


def __getattr__(algorithm_name: str):
    return fn(algorithm_name)
