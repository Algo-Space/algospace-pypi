#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-10-23 10:39:42
@LastEditors: Kermit
@LastEditTime: 2022-11-07 14:47:16
'''

import sys


def convert_text(txt: str) -> dict:
    return {'output_text': txt[::-1]}


if __name__ == '__main__':
    try:
        txt = sys.argv[1]
    except Exception as e:
        raise Exception('no arg')
    print(convert_text(txt))
