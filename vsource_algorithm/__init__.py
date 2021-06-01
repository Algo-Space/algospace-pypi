# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : __init__.py.py
# @Function : TODO

import os
import json
import time
import requests
import traceback

import vsource_algorithm.exceptions as exceptions
import vsource_algorithm.loginInstance as loginInstance
import vsource_algorithm.configs as configs

login_instance = loginInstance.LoginInstance()

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

def face_recognition(face_path1, face_path2):
    face_upload_url = configs.face_upload_url
    face_submit_url = configs.face_submit_url
    face_result_url = configs.face_result_url
    headers = {'Cookie': login_instance.cookie}
    with open(face_path1, 'rb') as f1:
        filename1 = os.path.split(face_path1)[-1]
        ext1 = os.path.splitext(face_path1)[-1]
        if ext1 not in ['.jpg', '.png']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 图像扩展名不对，请检查是否是png或者jpg')
        if ext1 == '.jpg':
            filetype = 'image/jpg'
        if ext1 == '.png':
            filetype = 'image/png'
        uploaded_response1 = requests.post(face_upload_url, files={
            'file':  (filename1, f1.read(), filetype)
        }, headers=headers)
        if uploaded_response1.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')

        uploaded_path1 = json.loads(uploaded_response1.content)['return_path']
    with open(face_path2, 'rb') as f2:
        filename2 = os.path.split(face_path2)[-1]
        ext2 = os.path.splitext(face_path2)[-1]
        if ext2 not in ['.jpg', '.png']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 图像扩展名不对，请检查是否是png或者jpg')
        if ext2 == '.jpg':
            filetype = 'image/jpg'
        if ext2 == '.png':
            filetype = 'image/png'
        uploaded_response2 = requests.post(face_upload_url, files={
            'file': (filename2, f2.read(), filetype)
        }, headers=headers)
        if uploaded_response1.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
        uploaded_path2 = json.loads(uploaded_response2.content)['return_path']
    post_params = {
        'face_name1': uploaded_path1,
        'face_name2': uploaded_path2
    }
    response = requests.post(face_submit_url, data=post_params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    task_id = response_dict['id']
    start_time = time.time()
    while True:
        # 轮询查询结果
        if time.time() - start_time >= configs.max_interval:
            raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')
        face_result = requests.get(face_result_url, params={'id': task_id}, headers=headers)
        face_ans = json.loads(face_result.content)
        if face_ans['status'] != 200:
            time.sleep(configs.interval)
            continue
        assert face_ans['status'] == 200
        return face_ans['result']['score']

    raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')


def speaker_recognition(speaker_path1, speaker_path2):
    speaker_upload_url = configs.speaker_upload_url
    speaker_submit_url = configs.speaker_submit_url
    speaker_result_url = configs.speaker_result_url
    headers = {'Cookie': login_instance.cookie}
    with open(speaker_path1, 'rb') as f1:
        filename1 = os.path.split(speaker_path1)[-1]
        ext1 = os.path.splitext(speaker_path1)[-1]
        if ext1 not in ['.wav']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 音频扩展名不对，请检查是否是wav格式')
        if ext1 == '.wav':
            filetype = 'audio/wav'
        uploaded_response1 = requests.post(speaker_upload_url, files={
            'file': (filename1, f1.read(), filetype)
        }, headers=headers)
        if uploaded_response1.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')

        uploaded_path1 = json.loads(uploaded_response1.content)['return_path']
    with open(speaker_path2, 'rb') as f2:
        filename2 = os.path.split(speaker_path2)[-1]
        ext2 = os.path.splitext(speaker_path2)[-1]
        if ext2 not in ['.wav']:
            raise exceptions.FileExtNotValid('[VSOURCE-Lib] 音频扩展名不对，请检查是否是wav格式')
        if ext2 == '.wav':
            filetype = 'audio/wav'
        uploaded_response2 = requests.post(speaker_upload_url, files={
            'file': (filename2, f2.read(), filetype)
        }, headers=headers)
        if uploaded_response1.status_code == 403:
            raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
        uploaded_path2 = json.loads(uploaded_response2.content)['return_path']
    post_params = {
        'speaker_name1': uploaded_path1,
        'speaker_name2': uploaded_path2
    }
    response = requests.post(speaker_submit_url, data=post_params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    task_id = response_dict['id']
    start_time = time.time()
    while True:
        # 轮询查询结果
        if time.time() - start_time >= configs.max_interval:
            raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')
        face_result = requests.get(speaker_result_url, params={'id': task_id}, headers=headers)
        face_ans = json.loads(face_result.content)
        if face_ans['status'] != 200:
            time.sleep(configs.interval)
            continue
        assert face_ans['status'] == 200
        return face_ans['result']['score']

    raise exceptions.TimeOutException('[VSOURCE-Lib] 请求超时，未知错误')


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

        uploaded_path = json.loads(uploaded_response.content)['return_path']
    image_params = {
        'image_path': uploaded_path
    }
    response = requests.get(face_detection_result_url, params=image_params, headers=headers)
    if response.status_code == 403:
        raise exceptions.LoginError('[VSOURCE-Lib] 登陆信息失败，请先正常的登陆')
    response_dict = json.loads(response.content)
    return response_dict
