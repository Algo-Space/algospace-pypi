import os
import json
import time
import requests
import traceback

import vsource.exceptions as exceptions
from vsource.loginInstance import login_instance
import vsource.configs as configs

def face_attribute(face_path, max_interval=configs.max_interval, version='none'):
    face_upload_url = configs.deepface_upload_url
    face_submit_url = configs.deepface_submit_url
    face_result_url = configs.deepface_result_url
    if version == 'fsx':
        face_upload_url = configs.deepface3_upload_url
        face_submit_url = configs.deepface3_submit_url
        face_result_url = configs.deepface3_result_url
    if version == 'cgy-2':
        face_upload_url = configs.deepface2_upload_url
        face_submit_url = configs.deepface2_submit_url
        face_result_url = configs.deepface2_result_url
    headers = {'Cookie': login_instance.cookie}
    with open(face_path, 'rb') as f1:
        filename1 = os.path.split(face_path)[-1]
        ext1 = os.path.splitext(face_path)[-1]
        if ext1 not in ['.jpg', '.png', '.jpeg']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 图像扩展名不对，请检查是否是png或者jpg')
        if ext1 == '.jpg':
            filetype = 'image/jpg'
        if ext1 == '.png':
            filetype = 'image/png'
        if ext1 == '.jpeg':
            filetype = 'image/jpeg'

        uploaded_response1 = requests.post(face_upload_url, files={
            'file':  (filename1, f1.read(), filetype)
        }, headers=headers)
        # print(uploaded_response1.content)
        if uploaded_response1.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')

        uploaded_path1 = json.loads(uploaded_response1.content)['return_path']

    post_params = {
        'face_name': uploaded_path1
    }
    response = requests.post(face_submit_url, data=post_params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    task_id = response_dict['id']
    start_time = time.time()
    while True:
        # 轮询查询结果
        if time.time() - start_time >= max_interval:
            raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')
        face_result = requests.get(face_result_url, params={'id': task_id}, headers=headers, timeout=max_interval)
        face_ans = json.loads(face_result.content)
        if face_ans['status'] != 200:
            time.sleep(configs.interval)
            continue
        try:
            assert face_ans['status'] == 200
            if face_ans['result']['status'] == 'error':
                return []
            return face_ans['result']['result']
        except Exception as e:
            return []

    raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')