#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 异常
@Author: Kermit
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-11-11 18:50:46
'''

class ConfigError(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)

class FileExtNotValid(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)


class TimeOutException(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)


class CallException(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)


class LoginError(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)


class InvalidAlgorithmVersion(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)