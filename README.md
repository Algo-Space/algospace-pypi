# 发布方本地部署指南

> 最保密、最快速的发布方式

> ⚡️⚡️⚡️ 一分钟极速发布 ⚡️⚡️⚡️

## 所需环境

👉 任何可以上网的计算机

👉 可以跑通的算法

👉 `Python>=3.7`

## 第一步：准备算法预测函数

例如：

```Python
def landmark_detection(image_path):
    ''' 
    人脸关键点标注
    args:
        image_path: 本地图片路径
    '''
    # 这里是具体算法实现 #
    return {
        'output_image_path': output_image_path,  # 带关键点标注的本地图片路径
        'dets': dets,                            # 目标图像检测的人脸坐标点
    }
```

## 第二步：安装 Python 包

在算法所用 Python 环境的命令行执行：

```Bash
pip install algospace -i https://pypi.python.org/simple
```

## 第三步：初始化配置文件

进入算法根目录，命令行执行：

```Bash
algospace init
```

> `algospace` 命令也可以简写为 `asc`

执行后在当前目录下生成 `algospace-config.py` 配置文件。

## 第四步：填写配置文件

根据 `algospace-config.py` 中的注释信息，填写第一步准备完成的预测函数的信息。

例如第一步预测函数的配置信息应当填写为：

```Python
service_filepath = './main.py'
service_function = 'landmark_detection'
service_input = {
    'image_path': {
        'type': 'image_path',
        'describe': '人脸图片',
    }
}
service_output = {
    'output_image_path': {
        'type': 'image_path',
        'describe': '带标注点的人脸图片'
    },
    'dets': {
        'type': 'str',
        'describe': '目标图像检测的人脸坐标点'
    }
}
```

## 最后一步：运行！

进入算法根目录，命令行执行：

```Bash
algospace start
```

也可以挂在后台运行：

```Bash
nohup algospace start > ./algospace.log 2>&1 &
```



**🎉 算法将会自动注册、运行、发布。**

**🎉 稍等片刻后即可在「我的算法」页面中查看新增的算法。**