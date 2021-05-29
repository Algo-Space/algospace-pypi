# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : loginInfoInsance.py
# @Function : TODO

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LoginInstance(metaclass=Singleton):
    def __init__(self, cookie=None):
        self.cookie = cookie

    def set_cookie(self, cookie):
        self.cookie = cookie
