# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : loginInfoInsance.py
# @Function : TODO

import json
import requests
import traceback
import vsource.configs as configs

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

login_instance = LoginInstance()

def login(username, password):
    try:
        login_url = configs.login_url
        login_data = {
            'username': username,
            'password': password
        }
        response = requests.post(login_url, data=login_data)
        response_dict = json.loads(response.content)
        if response_dict['status'] == 200:
            login_instance.set_cookie(response.headers['Set-Cookie'])
            return True
        return False
    except Exception as e:
        traceback.print_exc()
        return False