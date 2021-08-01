VSOURCE-Library
---------------

链接\ `VSOURCE\_FACE\_PLATFORM <https://github.com/VSOURCE-Platform/VSOURCE_FACE_PLATFORM>`__
，采用平台里的RESTFUL API提供一套本地能够使用的算法库。

.. code:: bash

    pip install vsource -i https://pypi.python.org/simple

目前功能：

1. 人脸识别：输入两张人脸图像判断来自一个人的概率
2. 说话人识别：输入两个音频判断来自一个人的概率
3. 人脸检测：输入一张图像检测出所有的人脸框图
4. 人脸属性：输入一张图像检测人脸并判断人脸的表情和年龄

一个人脸识别的Demo：

.. code:: python

    import vsource

    if __name__ == '__main__':
        username = {{ secrets.username }}
        password = {{ secrets.password }}
        vsource.login(username, password)

        face_path1 = 'examples/0006_01.jpg'
        face_path2 = 'examples/0007_01.jpg'
        score = vsource.face_recognition(face_path1, face_path2)
        print(score)

一个说话人识别的Demo:

.. code:: python

    import vsource

    if __name__ == '__main__':
        username = {{ serects.username }}
        password = {{ serects.password }}
        vsource.login(username, password)

        audio_path1 = 'examples/0.wav'
        audio_path2 = 'examples/1.wav'
        score = vsource.speaker_recognition(audio_path1, audio_path2)
        print(score)

一个人脸检测的Demo:

.. code:: python

    import vsource

    if __name__ == '__main__':
        username = {{ serects.username }}
        password = {{ serects.password }}
        vsource.login(username, password)

        face_path1 = 'examples/0008_01.jpg'
        result = vsource.face_detection(face_path1)
        print(result)

一个人脸属性的Demo:

.. code:: python

    import vsource

    if __name__ == '__main__':
        username = {{ serects.username }}
        password = {{ serects.password }}
        vsource.login(username, password)

        face_path1 = 'examples/0008_01.jpg'
        result = vsource.face_attribute(face_path1)
        print(result)
        # 其他同学实现的版本
        result2 = vsource.face_attribute(face_path1, version='fsx')
        print(result)

TIPS:

1. 关于用户名和密码，防止恶意的请求进入，导致服务器收到大量的请求后排队时间过长进一步让服务都不可用，所以暂时还是需要登录态，关于试用的用户名和密码可以联系我。
2. 持续的更新各种算法中。
3. 算法如果遇到超时，可以设置参数max\_interval=x秒，每个算法都带这个参数，比如face\_recognition(face\_path,
   max\_interval=100)。如果长时间没有结果，说明算法运行时出现了错误。
