## VSOURCE-Library

链接[VSOURCE_FACE_PLATFORM](https://github.com/VSOURCE-Platform/VSOURCE_FACE_PLATFORM) ，采用平台里的RESTFUL API提供一套本地能够使用的算法库。 

一个人脸识别的Demo：

```python
import vsource_algorithm

if __name__ == '__main__':
    username = {{ secrets.username }}
    password = {{ secrets.password }}
    vsource_algorithm.login(username, password)

    face_path1 = 'examples/0006_01.jpg'
    face_path2 = 'examples/0007_01.jpg'
    score = vsource_algorithm.face_recognition(face_path1, face_path2)
    print(score)
```

一个说话人识别的Demo:

```python
import vsource_algorithm

if __name__ == '__main__':
    username = {{ serects.username }}
    password = {{ serects.password }}
    vsource_algorithm.login(username, password)

    audio_path1 = 'examples/0.wav'
    audio_path2 = 'examples/1.wav'
    score = vsource_algorithm.speaker_recognition(audio_path1, audio_path2)
    print(score)
```

TIPS:

1. 关于用户名和密码，防止恶意的请求进入，导致服务器收到大量的请求后排队时间过长进一步让服务都不可用，所以暂时还是需要登录态，关于试用的用户名和密码可以联系我。
2. 持续的更新各种算法中。