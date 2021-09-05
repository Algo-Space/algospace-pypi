# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : demo.py
# @Function : TODO

import vsource
import requests
import time

if __name__ == '__main__':
    # username = {{ secrets.username }}
    # password = {{ secrets.password }}
    # vsource.login(username, password)

    username = 'api_user@vsource.club'
    password = 'my_api_user_123'
    vsource.login(username, password) # 先登录

    # # Face Recognition
    # face_path1 = 'examples/0008_01.jpg'
    # face_path2 = 'examples/0010_01.jpg'
    # score = vsource.face_recognition(face_path1, face_path2)
    # print(score)
    #
    # # Face Detection
    # face_path1 = 'examples/0008_01.jpg'
    # result = vsource.face_detection(face_path1)
    # print(result)

    # Speaker Recognition
    audio_path1 = 'examples/0.wav'
    audio_path2 = 'examples/1.wav'
    score = vsource.speaker_recognition(audio_path1, audio_path2, max_interval=10000)
    print(score)
    #
    # # Face Attribute
    # face_path1 = 'examples/0008_01.jpg'
    # result = vsource.face_attribute(face_path1, version='fsx')
    # print(result)

