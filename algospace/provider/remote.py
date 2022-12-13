#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-12-13 16:19:45
@LastEditors: Kermit
@LastEditTime: 2022-12-13 16:46:54
'''

from zipfile import ZipFile
import os


def upload_local_file_as_zip():
    ''' 以 zip 上传本地所有文件 '''
    root_path = os.getcwd()
    zip_name = 'algospace.zip'

    # 压缩工作目录所有文件和文件夹
    with ZipFile(zip_name, 'w') as zip_file:
        for root, _, files in os.walk(root_path):
            for file in files:
                if file == zip_name and root == root_path:
                    continue
                file_path = os.path.join(root, file)
                relative_path = file_path.replace(root_path, '')
                zip_file.write(file_path, relative_path)
