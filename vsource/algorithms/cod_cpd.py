# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : new_algorithm.py
# @Function : TODO


import os
import json
import time
import requests
import traceback

import vsource.exceptions as exceptions
from vsource.loginInstance import login_instance
import vsource.configs as configs

def cod_cpd(image_path, version='none', max_interval=configs.max_interval):
    if version == 'none':
        algorithm_name = 'cod_CPD'
        algorithm_version = '1.0.0'
        algorithm_port = 15127
    algorithm_ip   = '120.26.143.61'
    full_algorithm_name = algorithm_name + '-' + algorithm_version
    lower_name = full_algorithm_name.replace('-', '_').replace('.', '_').lower()
    upper_name = full_algorithm_name.replace('-', '_').replace('.', '_').upper()

    upload_url = 'http://{}/upload_files/tmp/tmp'.format(algorithm_ip)
    filename = os.path.split(image_path)[-1]
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f.read())}
    response = requests.post(upload_url, files=files)
    param_path = json.loads(response.content)['return_path']
    params = {
        'image_path': param_path
    }

    submit_url = 'http://{}:{}/{}_submit'.format(algorithm_ip, algorithm_port, lower_name)
    result_url = 'http://{}:{}//{}/get_result'.format(algorithm_ip, algorithm_port, lower_name)
    headers = {'Cookie': login_instance.cookie}
    response = requests.post(submit_url, data=params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    task_id = response_dict['id']
    start_time = time.time()
    while True:
        # 轮询查询结果
        if time.time() - start_time >= max_interval:
            raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')
        face_result = requests.get(result_url, params={'id': task_id}, headers=headers, timeout=max_interval)
        face_ans = json.loads(face_result.content)
        if face_ans['status'] != 200:
            time.sleep(configs.interval)
            continue
        assert face_ans['status'] == 200
        if face_ans['result']['status'] == 'error':
            return -1
        image_path = face_ans['result']['result']['res_path']
        final_image_path = 'http://{}/get_files/'.format(algorithm_ip) + image_path
        return final_image_path
    raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')