#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Ecohnoch(xcy)
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-11-27 19:40:06
'''

import json
import time
from typing import Optional
import requests
import traceback
import algospace.config as config
from algospace.exceptions import LoginError


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LoginInstance(metaclass=Singleton):
    def __init__(self, cookie: str = '', timestamp: int = 0):
        self.cookie = cookie
        self.timestamp = timestamp
        self.username = ''
        self.password = ''

    def ever_logined(self) -> bool:
        return self.username != '' and self.password != ''

    def is_outdated(self) -> bool:
        curr_timestamp = int(time.time())
        return curr_timestamp - self.timestamp > 10 * 24 * 60 * 60

    def set_cookie(self, cookie: str, timestamp: int) -> None:
        self.cookie = cookie
        self.timestamp = timestamp

    def get_cookie(self) -> str:
        if not self.ever_logined():
            raise LoginError('LoginError: No login before.')
        if self.is_outdated():
            self.login()
        return self.cookie

    def get_header(self) -> dict:
        return {'Cookie': self.get_cookie()}

    def login(self, username: Optional[str] = '', password: Optional[str] = '') -> bool:
        self.username = username or self.username
        self.password = password or self.password
        try:
            login_url = config.login_url
            login_data = {
                'user_id': self.username,
                'password': self.password
            }
            response = requests.post(login_url, data=login_data)
            if response.status_code != 200 and response.status_code != 201:
                raise Exception(response.status_code, response.content.decode())
            if response.json()['status'] != 200:
                raise Exception(response.json().get('err_msg', 'Login error.'))
            self.set_cookie(response.headers['Set-Cookie'], int(time.time()))
            return True
        except Exception as e:
            traceback.print_exc()
            return False


login_instance = LoginInstance()
login = login_instance.login
