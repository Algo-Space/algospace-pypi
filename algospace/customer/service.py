#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-11-11 15:27:48
@LastEditors: Kermit
@LastEditTime: 2022-11-11 22:04:55
'''


from typing import Optional
from algospace.exceptions import LoginError
from algospace.login import login as ori_login
from .config import call_timeout
from .fn import AlgoFunction


def login(username: str, password: str) -> None:
    ''' 登录 '''
    if not ori_login(username, password):
        raise LoginError('Login failed. Please check your password.')


_fn_storage = {}


def fn(algorithm_name: str, algorithm_version: Optional[str] = None, timeout: int = call_timeout) -> AlgoFunction:
    ''' 获取算法函数实例 '''
    global _fn_storage
    fn = _fn_storage.get(algorithm_name, {}).get(algorithm_version)
    if not fn:
        fn = AlgoFunction(algorithm_name, algorithm_version, timeout)
        fn_version = {algorithm_version: fn}
        _fn_storage[algorithm_name] = fn_version
    else:
        fn.timeout = timeout
    return fn


def call(algorithm_name: str, algorithm_version: Optional[str] = None, timeout: int = call_timeout, kwargs: dict = {}, **kwds: dict) -> dict:
    ''' 直接调用算法函数 '''
    kwargs.update(kwds)
    return fn(algorithm_name, algorithm_version, timeout)(**kwargs)


def show_example(algorithm_name: str, algorithm_version: Optional[str] = None):
    fn(algorithm_name, algorithm_version).show_example()


def info(algorithm_name: str, algorithm_version: Optional[str] = None) -> dict:
    ''' 获取算法信息 '''
    info = AlgoFunction(algorithm_name, algorithm_version).get_info()
    return {
        'name': info['name'],
        'version': info['version'],
        'can_call': info['can_call'],
        'input_param': info['input_param'],
        'output_param': info['output_param'],
        'create_date': info['create_date'],
        'example': info['example'],
        'output_example': info['output_example'],
    }


def clear_storage():
    ''' 清除算法信息缓存 '''
    global _fn_storage
    _fn_storage = {}
