# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : demo.py
# @Function : TODO

import vsource_algorithm

if __name__ == '__main__':
    username = {{ secrets.username }}
    password = {{ secrets.password }}
    vsource_algorithm.login(username, password)

    face_path1 = 'examples/0006_01.jpg'
    face_path2 = 'examples/0007_01.jpg'
    ans = vsource_algorithm.face_recognition(face_path1, face_path2)
    print(ans)