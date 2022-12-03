#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2022-12-03 21:10:13
'''

from typing import Callable
from . import config
from .config import Algoinfo
import urllib.request
import gradio as gr
import asyncio
import multiprocessing
from multiprocessing.synchronize import Lock
from multiprocessing.connection import Connection
import threading
import socket
import traceback
import requests
from algospace.login import login, login_instance
from .config_loader import ConfigLoader, valid_param_type
from .enroll import enroll, verify_config, is_component_normal
from .stdio import GradioPrint, QueueStdIO, QueueStdIOExec
import shutil
import json
import time
import os
import sys
import re


class ApiService:
    ''' 处理 Api 调用的 Service '''

    def __init__(self, algorithm_config: ConfigLoader, algorithm_info: Algoinfo) -> None:
        self.algorithm_config = algorithm_config
        self.algorithm_info = algorithm_info

    def read_file(self, path: str) -> str:
        ''' 将 storage 返回的 path 转换为本地 path '''
        file_url = self.algorithm_info.storage_file_url + '/' + path
        tmp_path = os.path.join(os.getcwd(), 'tmp')
        dir_path = os.path.dirname(os.path.join(tmp_path, path))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        file_request = urllib.request.Request(url=file_url,  method='GET')
        headers = login_instance.get_header()
        for key, value in headers.items():
            file_request.add_header(key, value)
        file_bytes = urllib.request.urlopen(file_request).read()

        with open(os.path.join(tmp_path, path), 'wb') as f:
            f.write(file_bytes)
        local_path = os.path.join(tmp_path, path)

        return local_path

    def write_file(self, local_path: str) -> str:
        ''' 将本地 path 转换为 storage 返回的 path '''
        filename = os.path.split(local_path)[-1]
        with open(local_path, 'rb') as f:
            files = {'file': (filename, f.read())}

        upload_url = f'{self.algorithm_info.storage_file_url}/{self.algorithm_info.name}/{self.algorithm_info.version}'
        response = requests.post(upload_url, files=files, headers=login_instance.get_header())
        if response.status_code != 200 and response.status_code != 201 and response.json()['status'] != 200:
            raise Exception('Failed to write file.')
        if type(response.json()['data']) != dict:
            raise Exception('Write file success but response has no \'data\'.')
        path = response.json()['data'].get('filepath')
        if path is None:
            raise Exception('Write file success but response has no \'filepath\'.')

        return path

    def get_input_type_class(self, type: str, ) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if type not in valid_param_type:
            raise Exception(f'Param type \'{type}\' is not available.')
        elif type == 'str':
            return str
        elif type == 'int':
            return int
        elif type == 'float':
            return float
        elif type == 'image_path':
            return self.read_file
        elif type == 'video_path':
            return self.read_file
        elif type == 'voice_path':
            return self.read_file
        else:
            return str

    def get_output_type_class(self, type: str, ) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if type not in valid_param_type:
            raise Exception(f'Param type \'{type}\' is not available.')
        elif type == 'str':
            return str
        elif type == 'int':
            return int
        elif type == 'float':
            return float
        elif type == 'image_path':
            return self.write_file
        elif type == 'video_path':
            return self.write_file
        elif type == 'voice_path':
            return self.write_file
        else:
            return str

    def handle(self, input_info: dict) -> dict:
        ''' 处理请求 '''
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Api Service] Begin to handle.')
        params = {}
        for key, info in self.algorithm_config.service_input.items():
            params[key] = self.get_input_type_class(info['type'])(input_info[key])
        out = self.algorithm_config.fn(**params)
        output_info = {}
        for key, info in self.algorithm_config.service_output.items():
            output_info[key] = self.get_output_type_class(info['type'])(out[key])
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Api Service] Complete.')
        return output_info

    def get_example(self):
        is_pure_name = re.match('^[a-zA-Z0-9_]*$', self.algorithm_config.name) is not None   # type: ignore
        if is_pure_name:
            example = f'algospace.{self.algorithm_config.name}'
        else:
            example = f'algospace.fn(\'{self.algorithm_config.name}\')'
        example += f'(' + ", ".join([f"{key}: {input_dict['type']}" for key,
                                     input_dict in self.algorithm_config.service_input.items()])+')'
        return example


class GradioService:
    ''' 处理 Gradio 的 Service '''

    def __init__(self, algorithm_config: ConfigLoader, algorithm_info: Algoinfo) -> None:
        self.algorithm_config = algorithm_config
        self.algorithm_info = algorithm_info

    def get_type_component(self, type: str, describe: str):
        ''' 获取处理每种类型的 Gradio component '''
        if type not in valid_param_type:
            raise Exception(f'Param type \'{type}\' is not available.')
        elif type == 'str':
            return gr.Textbox(placeholder=describe, label=describe)
        elif type == 'int':
            return gr.Number(precision=0, label=describe)
        elif type == 'float':
            return gr.Number(label=describe)
        elif type == 'image_path':
            return gr.Image(type='filepath', label=describe)
        elif type == 'video_path':
            return gr.Video(type='filepath', label=describe)
        elif type == 'voice_path':
            return gr.Audio(type='filepath', label=describe)
        else:
            return gr.Textbox(placeholder=describe)

    def launch(self, fn_lock: Lock, gradio_port_con: Connection) -> None:
        ''' 启动 Gradio 服务 '''
        def fn(*args):
            try:
                fn_lock.acquire()
                kwargs = {}
                for index, (key, _) in enumerate(self.algorithm_config.service_input.items()):
                    kwargs[key] = args[index]
                out = self.algorithm_config.fn(**kwargs)
                fn_lock.release()
                output_info = []
                for key, _ in self.algorithm_config.service_output.items():
                    output_info.append(out[key])
                return output_info if len(output_info) > 1 else output_info[0]
            except Exception:
                fn_lock.release()
                raise

        inputs = []
        for _, info in self.algorithm_config.service_input.items():
            inputs.append(self.get_type_component(info['type'], info['describe']))
        outputs = []
        for _, info in self.algorithm_config.service_output.items():
            outputs.append(self.get_type_component(info['type'], info['describe']))

        gr_interface = gr.Interface(
            title=self.algorithm_info.full_name,
            # description=self.algorithm_config.description,
            fn=fn,
            inputs=inputs,
            outputs=outputs,
        )

        self.check_port()
        threading.Thread(target=self.check_launched, args=(gradio_port_con,), daemon=True).start()

        with GradioPrint():
            gr_interface.launch(
                show_api=False,
                show_tips=False,
                favicon_path=None,
                inline=True,
                quiet=True,
                height=500,
                width=900,
                server_name=self.algorithm_config.gradio_server_host,
                server_port=self.algorithm_config.gradio_server_port
            )

    def check_port(self):
        ''' 检测可用端口 '''
        while (True):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            state = sock.connect_ex((self.algorithm_config.gradio_server_host,
                                    self.algorithm_config.gradio_server_port))
            sock.close()
            if state != 0:
                break
            self.algorithm_config.gradio_server_port += 1

    def check_launched(self, gradio_port_con: Connection):
        ''' 检测 Gradio 服务已经启动 '''
        while (True):
            time.sleep(1)
            try:
                html_text = requests.get(
                    f'http://{self.algorithm_config.gradio_server_host}:{self.algorithm_config.gradio_server_port}').text
                if len(html_text) == 0:
                    raise
                gradio_port_con.send(self.algorithm_config.gradio_server_port)
                gradio_port_con.close()
            except:
                pass

    def handle(self, input_info: dict) -> dict:
        ''' 处理请求 '''
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Gradio Service] Begin to handle.')

        req_method = input_info['method']
        req_apipath = input_info['apipath']
        req_headers = input_info['headers']
        req_query = input_info['query']
        req_body = input_info['body']
        req_is_body_json = input_info['is_body_json']
        if req_is_body_json:
            req_body = json.loads(req_body)
        url = f'http://{self.algorithm_config.gradio_server_host}:{self.algorithm_config.gradio_server_port}/{req_apipath}{"?" + req_query if req_query != "" else ""}'

        res = None
        if req_method == 'GET':
            res = requests.get(url)
        if req_method == 'POST' and req_headers['Content-Type'] == 'application/json':
            res = requests.post(url, json=req_body, headers=req_headers)
        if req_method == 'POST' and req_headers['Content-Type'] != 'application/json':
            res = requests.post(url, data=req_body, headers=req_headers)

        if res is not None:
            res_status_code = res.status_code
            res_headers = dict(res.headers)
            res_body = res.text
            result = {
                'status_code': res_status_code,
                'headers': res_headers,
                'body': res_body,
            }
        else:
            result = {}

        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Gradio Service] Complete.')
        return result

    def handle_init(self) -> dict:
        ''' 处理 Gradio 初始化请求 '''
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Gradio Init] Begin to handle.')

        if not os.path.exists('./frontend'):
            gradio_path = '/'.join(gr.__file__.split('/')[:-1])
            gradio_frontend_path = os.path.join(gradio_path, 'templates/frontend')
            shutil.copytree(gradio_frontend_path, './frontend')
            os.remove('./frontend/index.html')  # 删除未渲染的 index.html

        def upload_file(bashpath: str, subpath: str):
            ''' 递归上传文件夹里的文件 '''
            path = os.path.join(bashpath, subpath)
            if os.path.exists(os.path.join(path, '.DS_Store')):
                os.remove(os.path.join(path, '.DS_Store'))
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isdir(filepath):
                    upload_file(bashpath, os.path.join(subpath, filename))
                else:
                    url = self.algorithm_info.gradio_upload_url + '/' + subpath + '/' + filename
                    file = open(filepath, 'r', encoding="UTF-8", errors='ignore')
                    res = requests.post(url, files={'file': file}, headers=login_instance.get_header())
                    file.close()

        upload_file('./frontend', '.')

        if not os.path.exists('./frontend/index.html'):
            html_text = requests.get(
                f'http://{self.algorithm_config.gradio_server_host}:{self.algorithm_config.gradio_server_port}').text
            html_file = open('./frontend/index.html', 'w+', encoding="UTF-8", errors='ignore')
            html_file.write(html_text)
            html_file.close()
        url = self.algorithm_info.gradio_upload_url + '/index.html'
        file = open('./frontend/index.html', 'r', encoding="UTF-8", errors='ignore')
        res = requests.post(url, files={'file': file}, headers=login_instance.get_header())
        file.close()

        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Gradio Init] Complete.')
        return {}


class Service:
    ''' 算法提供方 Service '''

    def __init__(
        self,
        config_path: str,
    ):
        self.algorithm_config = ConfigLoader(config_path)
        self.algorithm_info = Algoinfo(self.algorithm_config.name, self.algorithm_config.version)

        self.login_headers = {}
        self.login_headers_timestamp = 0

        self.api_service = ApiService(self.algorithm_config, self.algorithm_info)
        self.gradio_service = GradioService(self.algorithm_config, self.algorithm_info)

    def launch_service(self, fn_lock: Lock, gradio_port_con: Connection):
        # 从管道接受 Gradio 运行成功的端口
        gradio_port = int(gradio_port_con.recv())
        gradio_port_con.close()
        self.algorithm_config.gradio_server_port = gradio_port

        # 开始处理
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] [Service] Your algorithm site: {self.algorithm_info.algorithm_site}')
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] [Service] Start handling...')
        print('')
        while True:
            try:
                # 轮询一条请求消息
                ask_for_data_resp = requests.get(self.algorithm_info.ask_data_url, headers=login_instance.get_header())
                if ask_for_data_resp.status_code != 200 and ask_for_data_resp.status_code != 201:
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                          '[Service] Ask data error:', ask_for_data_resp.status_code,
                          ask_for_data_resp.content.decode())
                    continue
                ask_for_data_dict = ask_for_data_resp.json()
                if ask_for_data_dict['status'] == 201:
                    # 没有新的请求信息
                    time.sleep(config.call_interval)
                    continue
                if ask_for_data_dict['status'] != 200:
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                          '[Service] Ask data error: the response', ask_for_data_dict)
                    continue
                req_info = ask_for_data_dict.get('data', {})
                if type(req_info) != dict:
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                          '[Service] Ask data error: the property of \'data\' is not dict.')
                    continue
                req_info = req_info.get('req_info', {})
                if type(req_info) != dict:
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                          '[Service] Ask data error: the property of \'req_info\' is not dict.')
                    continue

                try:
                    # 根据请求类型处理
                    if req_info['type'] == 'api':
                        # 处理计算请求
                        try:
                            fn_lock.acquire()
                            result = self.api_service.handle(req_info['data'])
                            fn_lock.release()
                        except:
                            fn_lock.release()
                            raise
                    elif req_info['type'] == 'gradio':
                        # 处理 Gradio 请求
                        result = self.gradio_service.handle(req_info['data'])
                    elif req_info['type'] == 'gradio_init':
                        # 处理 Gradio 初始化请求
                        result = self.gradio_service.handle_init()
                    else:
                        result = {}

                    # 回传数据
                    res_info = {
                        'id': req_info['id'],
                        'type': req_info['type'],
                        'status': 'finished',
                        'owner': req_info['owner'],
                        'create_date': req_info['create_date'],
                        'result': result
                    }
                    return_ans_param = {'res_info': res_info}
                    return_ans_resp = requests.post(self.algorithm_info.return_ans_url,
                                                    json=return_ans_param, headers=login_instance.get_header())

                    if return_ans_resp.status_code != 200 and return_ans_resp.status_code != 201 and return_ans_resp.json()['status'] != 200:
                        err_msg = "Service Result Return Error."
                        raise Exception(err_msg)
                    else:
                        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                              '[Service] Return ans success.')
                except Exception as e:
                    traceback.print_exc()
                    # 回传失败数据
                    res_info = {
                        'id': req_info['id'],
                        'type': req_info['type'],
                        'status': 'error',
                        'owner': req_info['owner'],
                        'create_date': req_info['create_date'],
                        'result': {'err_msg': str(e)}
                    }
                    return_error_param = {'res_info': res_info}
                    requests.post(self.algorithm_info.return_err_url, json=return_error_param,
                                  headers=login_instance.get_header())
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                          '[Service] Return error ans success.')

                if os.path.exists('tmp'):
                    shutil.rmtree('tmp')
            except Exception as e:
                traceback.print_exc()
                print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[Service] Handle error:', str(e))
                time.sleep(config.call_interval)
                continue

    def launch(self, stdout_queueu: multiprocessing.Queue, stderr_queueu: multiprocessing.Queue, type: str, fn_lock: Lock, gradio_port_con: Connection):
        sys.stdout = QueueStdIO(sys.stdout, stdout_queueu)
        sys.stderr = QueueStdIO(sys.stderr, stderr_queueu)
        if not self.login():
            exit(1)
        if type == 'SERVICE':
            self.launch_service(fn_lock, gradio_port_con)
        elif type == 'GRADIO':
            self.gradio_service.launch(fn_lock, gradio_port_con)
        else:
            raise Exception('Argument "type" is unaccessable.')

    def login(self):
        if not login(self.algorithm_config.username, self.algorithm_config.password):
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                  f'[{self.algorithm_info.upper_name}] Login failed. Please check your password.')
            return False
        return True

    def enroll(self):
        try:
            enroll(self.algorithm_config.name, self.algorithm_config.version, self.algorithm_config.service_input, self.algorithm_config.service_output,
                   self.algorithm_config.description, self.algorithm_config.scope, self.algorithm_config.chinese_name, self.algorithm_config.document, self.algorithm_config.config_file_content)
            return True
        except Exception as e:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                  f'[{self.algorithm_info.upper_name}] Enroll failed:', str(e))
            return False

    def verify_config(self):
        try:
            file = verify_config(self.algorithm_config.name, self.algorithm_config.version, self.algorithm_config.service_input,
                                 self.algorithm_config.service_output)
            if file:
                dirpath = os.path.dirname(self.algorithm_config.config_path)
                filepath = os.path.join(dirpath, 'algospace-config-origin.py')
                with open(filepath, 'w') as f:
                    f.write(file)
                print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                      f'[{self.algorithm_info.upper_name}] Content of \'{self.algorithm_config.config_path}\' is not same as the config enrolled before. The original config file is regenerated at \'{filepath}\'. Please use the original file to start. Or if you have modified the algorithm, use a new \'version\' to start.')
                return False
            return True
        except Exception as e:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                  f'[{self.algorithm_info.upper_name}] Verify config failed:', str(e))
            return False

    def is_component_normal(self):
        while (True):
            if is_component_normal(self.algorithm_config.name, self.algorithm_config.version):
                break
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
                  f'[{self.algorithm_info.upper_name}] Waiting for components started...')
            time.sleep(5)

    def send_heartbeat(self):
        body = {
            'algorithm_name': self.algorithm_info.name,
            'algorithm_version': self.algorithm_info.version
        }
        requests.post(self.algorithm_info.heartbeat_url, data=body, headers=login_instance.get_header())

    async def start(self):
        # 初始化状态
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
              f'[{self.algorithm_info.upper_name}] Initializing...')
        if not self.login():
            return
        if not self.enroll():
            return
        if not self.verify_config():
            return
        self.is_component_normal()

        # 开启子进程
        stdout_queueu = multiprocessing.Queue(maxsize=0)  # 子进程通过队列将标准输出重定向到父进程
        stderr_queueu = multiprocessing.Queue(maxsize=0)  # 子进程通过队列将标准输出重定向到父进程
        fn_lock = multiprocessing.Lock()  # 模型函数的锁
        gradio_port_con1, gradio_port_con2 = multiprocessing.Pipe()  # 传递 Gradio 端口的管道

        def create_service_process():
            service_process = multiprocessing.Process(target=self.launch, args=(
                stdout_queueu, stderr_queueu, 'SERVICE', fn_lock, gradio_port_con2), daemon=True)
            service_process.start()
            return service_process

        def create_gradio_process():
            gradio_process = multiprocessing.Process(target=self.launch, args=(
                stdout_queueu, stderr_queueu, 'GRADIO', fn_lock, gradio_port_con1), daemon=True)
            gradio_process.start()
            return gradio_process

        def check_process_alive(process: multiprocessing.Process):
            is_alive = process.is_alive
            if not is_alive:
                process.kill()
            return is_alive

        service_process = create_service_process()
        gradio_process = create_gradio_process()

        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]',
              f'[{self.algorithm_info.upper_name}] Waiting for service launched...')

        # 开启事件循环
        async def heartbeat_task():
            times = 0
            while True:
                if times % 10 == 0:
                    # 每 10 秒发送心跳
                    await asyncio.get_running_loop().run_in_executor(None, self.send_heartbeat)
                    times = 0
                await asyncio.sleep(1)
                times += 1

        async def alive_task():
            nonlocal service_process
            nonlocal gradio_process
            while True:
                await asyncio.sleep(1)
                if not check_process_alive(service_process):
                    service_process = create_service_process()
                if not check_process_alive(gradio_process):
                    gradio_process = create_service_process()

        async def subprocess_stdout_task():
            stdout_exec = QueueStdIOExec(sys.stdout, stdout_queueu).exec
            while True:
                await asyncio.get_running_loop().run_in_executor(None, stdout_exec)

        async def subprocess_stderr_task():
            stderr_exec = QueueStdIOExec(sys.stderr, stderr_queueu).exec
            while True:
                await asyncio.get_running_loop().run_in_executor(None, stderr_exec)

        tasks = [heartbeat_task(), alive_task(), subprocess_stdout_task(), subprocess_stderr_task()]
        await asyncio.wait(tasks)


def run_service(config_path: str) -> None:
    try:
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Init.')
        service = Service(config_path)
        asyncio.run(service.start())
    except:
        traceback.print_exc()
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', '[AlgoSpace] Exit.')
