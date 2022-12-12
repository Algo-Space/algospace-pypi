''' AlgoSpace 算法服务配置文件 '''

############################
# 必填选项:
#   - name:                 算法名，仅能包含英文字母、数字和 _ - @ 符号
#   - version:              算法版本，仅能包含英文字母、数字和 . 符号
#   - username:             登录名
#   - password:             密码
#   - service_filepath:     算法服务文件路径，相对于本文件路径
#   - service_function:     算法服务函数名
#   - service_input:        算法服务函数输入参数，字典类型
#       - .{arg}:           参数名
#       - .{arg}.type:      参数类型，包含: str (字符串), int (定点数), float (浮点数), image_path (图片本地路径), video_path (视频本地路径), voice_path (音频本地路径)
#       - .{arg}.describe:  参数简要描述
#   - service_output:       算法服务函数输出参数，字典类型，函数需以对应字典类型输出
#       - .{arg}:           参数名
#       - .{arg}.type:      参数类型，包含: str (字符串), int (定点数), float (浮点数), image_path (图片本地路径), video_path (视频本地路径), voice_path (音频本地路径)
#       - .{arg}.describe:  参数简要描述
#   - service_timeout:      算法服务超时时间，单位: 秒
#   - service_max_parallel: 算法服务最大同时处理请求数；若大于 1，则需要保证算法服务函数处理时的线程安全，否则请通过多实例部署算法
#   - service_tmp_dir:      算法服务临时文件存放文件夹的路径，相对于本文件路径，用于函数输入参数包含 image_path, video_path, voice_path 时存放临时文件
#
# 参数配置填写示例:
#   示例函数:
#       def example_fn(text, image):
#           # 这里是具体算法实现 #
#           return { 'result_text': ..., 'result_image': ... }
#   对应参数配置:
#       service_input = {
#           'text': {
#               'type': 'str',
#               'describe': '输入一段文字',
#           },
#           'image': {
#               'type': 'image_path',
#               'describe': '输入一张图片',
#           }
#       }
#       service_output = {
#           'result_text': {
#               'type': 'str',
#               'describe': '文字返回结果'
#           },
#           'result_image': {
#               'type': 'image_path',
#               'describe': '图片返回结果'
#           }
#       }
############################

name = 'example_name'
version = 'v1.0'
username = 'user'
password = '****'
service_filepath = './main.py'
service_function = 'example_fn'
service_input = {
    'arg0': {
        'type': 'str',
        'describe': '',
    }
}
service_output = {
    'arg0': {
        'type': 'str',
        'describe': ''
    }
}
service_timeout = 60
service_max_parallel = 1
service_tmp_dir = './tmp'

############################
# 算法详情选项，可在网页端进行修改:
#   - description:          描述算法的简介，简要介绍算法的要点，可选格式：纯文本、HTML
#   - scope:                算法可见范围，可选值：PRIVATE（自己可见）、GROUP（小组内可见）、INSTITUTION（机构内可见）、PUBLIC（公开）
#   - chinese_name:         中文名，将与算法名一同向用户展示
#   - document_filepath:    文档文件路径，详细介绍算法的要点，可选格式：纯文本、Markdown、HTML，相对于本文件路径，如：'./README.md'
############################

description = ''
scope = 'PRIVATE'
chinese_name = ''
document_filepath = ''

############################
# 容器式部署选项，用于 generate 命令生成 docker 相关配置:
#   - requirements: 依赖包，如 ['torch', 'numpy', 'matplotlib==3.6.2']
#   - pre_command:  容器用于配置环境的命令，构建镜像时依次执行，如 ['apt install -y libgl1-mesa-glx']
#   - base_image:   构建容器镜像的基础镜像，默认使用 python:3.9
############################

requirements = []
pre_command = []
base_image = 'python:3.9'

############################
# 需要自主实现更复杂的 Gradio 应用时，可使用以下选项替代自动生成的 Gradio 应用:
#   - gradio_launch_filepath: 自主实现的 Gradio 入口文件路径，相对于本文件路径，如：'./gradio_launch.py'
#   - gradio_launch_function: 自主实现的 Gradio 入口函数名，如：'gradio_launch'，入口函数应当不含任何参数
#   - gradio_launch_host:     自主实现的 Gradio 服务器地址，同 Gradio 的 GRADIO_SERVER_NAME 配置，默认：'127.0.0.1'
#   - gradio_launch_port:     自主实现的 Gradio 端口号，同 Gradio 的 GRADIO_SERVER_PORT 配置，默认：7860
#
# 提示：
#   同一版本的算法，不可有多种 Gradio 的实现代码；
#   若修改 Gradio 的实现代码，请以新版本号启动。
############################

gradio_launch_filepath = ''
gradio_launch_function = ''
gradio_launch_host = '127.0.0.1'
gradio_launch_port = 7860
