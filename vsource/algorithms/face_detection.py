import os
import json
import time
import requests
import traceback

import vsource.exceptions as exceptions
from vsource.loginInstance import login_instance
import vsource.configs as configs

def face_detection(face_path):
    face_detection_upload_url = configs.face_detection_upload_url
    face_detection_result_url = configs.face_detection_result_url
    headers = {'Cookie': login_instance.cookie}
    with open(face_path, 'rb') as f:
        filename = os.path.split(face_path)[-1]
        ext = os.path.splitext(face_path)[-1]
        if ext not in ['.jpg', '.png']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 图像扩展名不对，请检查是否是png或者jpg')
        if ext == '.jpg':
            filetype = 'image/jpg'
        if ext == '.png':
            filetype = 'image/png'
        uploaded_response = requests.post(face_detection_upload_url, files={
            'file':  (filename, f.read(), filetype)
        }, headers=headers)
        if uploaded_response.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
        print(uploaded_response.content)
        uploaded_path = json.loads(uploaded_response.content)['return_path']
    image_params = {
        'image_path': uploaded_path
    }
    response = requests.get(face_detection_result_url, params=image_params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    return response_dict