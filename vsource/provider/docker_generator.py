#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: Docker 配置生成器
@Author: Kermit
@Date: 2022-11-11 13:21:18
@LastEditors: Kermit
@LastEditTime: 2022-11-11 15:20:28
'''

import traceback
import os
from .config_loader import ConfigLoader
from .config import Algoinfo


def generate_docker_config(config_path: str):
    try:
        algorithm_config = ConfigLoader(config_path)
        algorithm_info = Algoinfo(algorithm_config.name, algorithm_config.version)

        gen_requirements_txt(algorithm_config.requirements)
        print('[Vsource] [Step 1/4] Requirements has been successfully generated!')
        gen_dockerfile(algorithm_config.pre_command, algorithm_config.base_image, config_path)
        print('[Vsource] [Step 2/4] Dockerfile has been successfully generated!')
        gen_docker_compose(algorithm_info.name, algorithm_info.version, algorithm_info.lower_name)
        print('[Vsource] [Step 3/4] Docker compose file has been successfully generated!')
        gen_control_script(algorithm_info.name, algorithm_info.version)
        print('[Vsource] [Step 4/4] Docker control file has been successfully generated!')
        print(f'[Vsource] Generate successfully! Name: {algorithm_config.name}, Version: {algorithm_config.version}')
    except Exception as e:
        traceback.print_exc()
        print('[Vsource] Generate error:', *e.args)


def gen_requirements_txt(requirements: list[str]):
    requirements.append('vsource')
    with open('vsource-requirements.txt', 'w') as f:
        for requirements_item in requirements:
            if 'torch==' in requirements_item.replace(' ', ''):
                # 如果是Pytorch，要从官网下载可支持版本，否则会出问题，查看 Dockerfile 那里
                f.write('--find-links https://download.pytorch.org/whl/torch_stable.html\n')
                f.write(requirements_item + '\n')
            elif 'torchvision' in requirements_item:
                f.write('--find-links https://download.pytorch.org/whl/torch_stable.html\n')
                f.write(requirements_item + '\n')
            else:
                f.write(requirements_item + '\n')


def gen_dockerfile(pre_command: list[str], base_image: str, config_path: str):
    with open(os.path.join(os.path.split(__file__)[0], 'templates', 'docker', 'vsource-dockerfile'), 'r') as f:
        template = f.read()

    pre_command_lines = ''
    for index, command_item in enumerate(pre_command):
        if index < len(pre_command) - 1:
            pre_command_lines += (f'    {command_item} && \\\n')
        else:
            pre_command_lines += (f'    {command_item}')
    template = template.replace('{PRE_COMMAND}', pre_command_lines)
    template = template.replace('{BASE_IMAGE}', base_image)
    template = template.replace('{CONFIG_PATH}', config_path)

    with open(os.path.join('vsource-dockerfile'), 'w') as f:
        f.write(template)


def gen_docker_compose(name: str, version: str, lower_name: str):
    with open(os.path.join(os.path.split(__file__)[0], 'templates', 'docker', 'vsource-docker-compose.yml'), 'r') as f:
        template = f.read()

    template = template.replace('{ALGORITHM_LOWER_NAME}', lower_name)
    template = template.replace('{ALGORITHM_NAME}', name)
    template = template.replace('{ALGORITHM_VERSION}', version)

    with open(os.path.join('vsource-docker-compose.yml'), 'w') as f:
        f.write(template)


def gen_control_script(name: str, version: str):
    with open(os.path.join(os.path.split(__file__)[0], 'templates', 'docker', 'vsource-docker-start.sh'), 'r') as f:
        template = f.read()
    with open(os.path.join('vsource-docker-start.sh'), 'w') as f:
        template = template.replace('{ALGORITHM_NAME}', name)
        template = template.replace('{ALGORITHM_VERSION}', version)
        f.write(template)

    with open(os.path.join(os.path.split(__file__)[0], 'templates', 'docker', 'vsource-docker-stop.sh'), 'r') as f:
        template = f.read()
    with open(os.path.join('vsource-docker-stop.sh'), 'w') as f:
        f.write(template)

    with open(os.path.join(os.path.split(__file__)[0], 'templates', 'docker', 'vsource-docker-logs.sh'), 'r') as f:
        template = f.read()
    with open(os.path.join('vsource-docker-logs.sh'), 'w') as f:
        f.write(template)
