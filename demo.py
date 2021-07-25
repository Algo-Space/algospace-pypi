# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : demo.py
# @Function : TODO

import vsource_algorithm
import requests
import time

if __name__ == '__main__':
    username = {{ secrets.username }}
    password = {{ secrets.password }}
    vsource_algorithm.login(username, password)

    # Face Recognition
    face_path1 = 'examples/0008_01.jpg'
    face_path2 = 'examples/0010_01.jpg'
    score = vsource_algorithm.face_recognition(face_path1, face_path2)
    print(score)

    # Face Detection
    face_path1 = 'examples/0008_01.jpg'
    result = vsource_algorithm.face_detection(face_path1)
    print(result)

    # Speaker Recognition
    audio_path1 = 'examples/0.wav'
    audio_path2 = 'examples/1.wav'
    score = vsource_algorithm.speaker_recognition(audio_path1, audio_path2)
    print(score)

    # Face Attribute
    face_path1 = 'examples/0008_01.jpg'
    result = vsource_algorithm.face_attribute(face_path1)
    print(result)

