''' AlgoSpace 算法服务配置文件 '''

############################
# 必填选项:
#   - name:                 算法名，仅能包含英文字母、数字和 _ - @ 符号
#   - version:              算法版本：仅能包含英文字母、数字和 . 符号
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

############################
# 可选选项:
#   - description:          描述算法的简介，简要介绍算法的要点
#   - scope:                算法可见范围，可选值：PRIVATE（自己可见）、GROUP（小组内可见）、INSTITUTION（机构内可见）、PUBLIC（公开）
#   - chinese_name:         中文名，将与算法名一同向用户展示
#   - document_filepath:    文档文件路径，详细介绍算法的要点，可选格式：纯文本、Markdown、HTML，相对于本文件路径，如：'./README.md'
############################

description = ''
scope = 'PRIVATE'
chinese_name = ''
document_filepath = ''

############################
# 容器式部署选项（用于 generate 命令生成 docker 相关配置）:
#   - requirements: 依赖包，如 ['torch', 'numpy', 'matplotlib==3.6.2']
#   - pre_command:  容器用于配置环境的命令，构建镜像时依次执行，如 ['apt install -y libgl1-mesa-glx']
#   - base_image:   构建容器镜像的基础镜像，默认使用 python:3.9
############################

requirements = []
pre_command = []
base_image = ''
