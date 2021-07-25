# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : __init__.py.py
# @Function : TODO

class FileExtNotValid(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)

class TimeOutException(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)

class LoginError(Exception):
    def __init__(self, err_msg):
        Exception.__init__(self, err_msg)