#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 算法提供者核心服务
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2023-02-03 20:52:02
'''

from typing import Callable, Optional, List, Tuple, Union
from algospace.logger import Logger, algospace_logger
from algospace.util import create_timestamp_filename
from . import config
from .config import Algoinfo
import urllib.request
import gradio as gr
import asyncio
import multiprocessing
from multiprocessing.synchronize import Lock
from multiprocessing.connection import Connection
import threading
import concurrent.futures
import socket
import traceback
import requests
import websocket
from algospace.login import login, login_instance
from .config_loader import ConfigLoader, InputType, OutputType, valid_input_type, valid_output_type
from .enroll import enroll, verify_config, is_component_normal
from .stdio import GradioPrint, QueueStdIO, QueueStdIOExec
import shutil
import json
import time
import os
import re
import base64
import binascii


class FnService:
    ''' 模型函数 Service '''

    def __init__(self, algorithm_config: ConfigLoader) -> None:
        self.algorithm_config = algorithm_config
        self.logger = Logger('Fn Service', is_show_time=True)

    async def handle(self, *args, **kwargs):
        ''' 处理函数请求 '''
        future = asyncio.get_event_loop().run_in_executor(None, lambda: self.algorithm_config.fn(*args, **kwargs))
        out = await asyncio.wait_for(future, timeout=self.algorithm_config.service_timeout)
        return out

    def launch_thread(self, fn_index: int, fn_req_queue: multiprocessing.Queue, fn_res_queue: multiprocessing.Queue) -> None:
        ''' 启动函数服务线程 '''
        while True:
            try:
                args, kwargs = fn_req_queue.get()
                self.logger.info(f'[{fn_index}] Begin to calculate.')
                out = asyncio.run(self.handle(*args, **kwargs))
                self.logger.info(f'[{fn_index}] Complete.')
                fn_res_queue.put((out, None))
            except Exception as e:
                fn_res_queue.put((None, e))

    def launch(self,
               fn_req_queue_list: List[multiprocessing.Queue],
               fn_res_queue_list: List[multiprocessing.Queue]) -> None:
        ''' 启动函数服务 '''
        # 校验函数配置并附带将函数 import 入进程
        self.algorithm_config.verify_service()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            pool.map(self.launch_thread,
                     [i for i in range(len(fn_req_queue_list))],
                     [fn_req_queue_list[i] for i in range(len(fn_req_queue_list))],
                     [fn_res_queue_list[i] for i in range(len(fn_res_queue_list))])


def get_available_fn_queue(
        fn_lock_list: List[Lock],
        fn_req_queue_list: List[multiprocessing.Queue],
        fn_res_queue_list: List[multiprocessing.Queue]) -> Tuple[Lock, multiprocessing.Queue, multiprocessing.Queue]:
    ''' 获取当前可用的函数锁、函数队列 '''
    for i in range(len(fn_lock_list)):
        if fn_lock_list[i].acquire(block=False):
            return fn_lock_list[i], fn_req_queue_list[i], fn_res_queue_list[i]
    raise Exception('No available fn queue.')


class ApiService:
    ''' 处理 Api 调用的 Service '''

    def __init__(self, algorithm_config: ConfigLoader, algorithm_info: Algoinfo) -> None:
        self.algorithm_config = algorithm_config
        self.algorithm_info = algorithm_info
        self.logger = Logger('Api Service', is_show_time=True)

    def read_file(self, dict_or_path: Union[dict, str]) -> str:
        ''' 将文件字典或 storage 返回的 path 转换为本地文件并返回本地文件路径 '''
        if type(dict_or_path) == dict:
            file_dict: dict = dict_or_path  # type: ignore
            file_name = create_timestamp_filename() + '.' + \
                file_dict.get('format', '') if file_dict.get('format') else create_timestamp_filename()

            if file_dict.get('type', 'base64') == 'base64':
                file_bytes = base64.b64decode(file_dict.get('data', ''), validate=True)
            elif file_dict.get('type', 'base64') == 'url':
                file_bytes = requests.get(file_dict.get('data', '')).content
            else:
                raise Exception(f'Invalid file type: {file_dict.get("type")}, only support base64 and url.')
        else:
            # 兼容旧版本: 传入的是 storage 返回的 path
            path: str = dict_or_path  # type: ignore
            file_name = path.split('/')[-1]
            file_url = config.storage_file_url + '/' + path
            file_request = urllib.request.Request(url=file_url,  method='GET')
            headers = login_instance.get_header()
            for key, value in headers.items():
                file_request.add_header(key, value)
            file_response = urllib.request.urlopen(file_request)
            file_bytes = file_response.read()

        tmp_path = self.algorithm_config.service_tmp_path
        local_path = os.path.join(tmp_path, file_name)
        dir_path = os.path.dirname(local_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(local_path, 'wb') as f:
            f.write(file_bytes)

        return local_path

    def write_file(self, local_path: str) -> str:
        ''' 将本地 path 转换为 storage 返回的 path '''
        filename = os.path.split(local_path)[-1]
        with open(local_path, 'rb') as f:
            files = {'file': (filename, f.read())}

        upload_url = f'{config.storage_file_url}/{self.algorithm_info.name}/{self.algorithm_info.version}'
        response = requests.post(upload_url, files=files, headers=login_instance.get_header())
        if response.status_code != 200 and response.status_code != 201 and response.json()['status'] != 200:
            raise Exception('Failed to write file.')
        if type(response.json()['data']) != dict:
            raise Exception('Write file success but response has no \'data\'.')
        path = response.json()['data'].get('filepath')
        if path is None:
            raise Exception('Write file success but response has no \'filepath\'.')

        return path

    def get_input_type_class(self, input_type: str) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if input_type not in valid_input_type:
            raise Exception(f'Input type \'{input_type}\' is not available.')
        elif input_type == InputType.STRING:
            return str
        elif input_type == InputType.INTEGER:
            return int
        elif input_type == InputType.FLOAT:
            return float
        elif input_type == InputType.IMAGE_PATH:
            return self.read_file
        elif input_type == InputType.VIDEO_PATH:
            return self.read_file
        elif input_type == InputType.VOICE_PATH:
            return self.read_file
        else:
            return str

    def get_output_type_class(self, output_type: str) -> Callable:
        ''' 获取处理每种类型的 Callable 对象 '''
        if output_type not in valid_output_type:
            raise Exception(f'Output type \'{output_type}\' is not available.')
        elif output_type == OutputType.STRING:
            return str
        elif output_type == OutputType.INTEGER:
            return int
        elif output_type == OutputType.FLOAT:
            return float
        elif output_type == OutputType.IMAGE_PATH:
            return self.write_file
        elif output_type == OutputType.VIDEO_PATH:
            return self.write_file
        elif output_type == OutputType.VOICE_PATH:
            return self.write_file
        else:
            return str

    def handle(self,
               input_info: dict,
               fn_lock_list: List[Lock],
               fn_req_queue_list: List[multiprocessing.Queue],
               fn_res_queue_list: List[multiprocessing.Queue]) -> dict:
        ''' 处理请求 '''
        self.logger.info('Begin to handle.')
        params = {}
        for key, info in self.algorithm_config.service_input.items():
            params[key] = self.get_input_type_class(info['type'])(input_info[key])

        fn_lock = None
        try:
            fn_lock, fn_req_queue, fn_res_queue = get_available_fn_queue(
                fn_lock_list, fn_req_queue_list, fn_res_queue_list)
            fn_req_queue.put(((), params))
            out, e = fn_res_queue.get()
            if e is not None:
                raise e
        finally:
            if fn_lock is not None:
                fn_lock.release()

        output_info = {}
        for key, info in self.algorithm_config.service_output.items():
            output_info[key] = self.get_output_type_class(info['type'])(out[key])
        self.logger.info('Complete.')
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
        self.gradio_upload_url = None
        self.logger = Logger('Gradio Service', is_show_time=True)
        self.init_logger = Logger('Gradio Init', is_show_time=True)

    def get_input_component(self, input_type: str, describe: str):
        ''' 获取处理每种类型的 Gradio component '''
        if input_type not in valid_input_type:
            raise Exception(f'Input type \'{input_type}\' is not available.')
        elif input_type == InputType.STRING:
            return gr.Textbox(placeholder=describe, label=describe)
        elif input_type == InputType.INTEGER:
            return gr.Number(precision=0, label=describe)
        elif input_type == InputType.FLOAT:
            return gr.Number(label=describe)
        elif input_type == InputType.IMAGE_PATH:
            return gr.Image(type='filepath', label=describe)
        elif input_type == InputType.VIDEO_PATH:
            return gr.Video(type='filepath', label=describe)
        elif input_type == InputType.VOICE_PATH:
            return gr.Audio(type='filepath', label=describe)
        else:
            return gr.Textbox(placeholder=describe)

    def get_output_component(self, output_type: str, describe: str):
        ''' 获取处理每种类型的 Gradio component '''
        if output_type not in valid_output_type:
            raise Exception(f'Output type \'{output_type}\' is not available.')
        elif output_type == OutputType.STRING:
            return gr.Textbox(placeholder=describe, label=describe)
        elif output_type == OutputType.INTEGER:
            return gr.Number(precision=0, label=describe)
        elif output_type == OutputType.FLOAT:
            return gr.Number(label=describe)
        elif output_type == OutputType.IMAGE_PATH:
            return gr.Image(type='filepath', label=describe)
        elif output_type == OutputType.VIDEO_PATH:
            return gr.Video(type='filepath', label=describe)
        elif output_type == OutputType.VOICE_PATH:
            return gr.Audio(type='filepath', label=describe)
        else:
            return gr.Textbox(placeholder=describe)

    def launch(self,
               fn_lock_list: List[Lock],
               fn_req_queue_list: List[multiprocessing.Queue],
               fn_res_queue_list: List[multiprocessing.Queue],
               gradio_port_con: Connection) -> None:
        ''' 启动 Gradio 服务 '''
        def fn(*args):
            kwargs = {}
            for index, (key, _) in enumerate(self.algorithm_config.service_input.items()):
                kwargs[key] = args[index]

            fn_lock = None
            try:
                fn_lock, fn_req_queue, fn_res_queue = get_available_fn_queue(
                    fn_lock_list, fn_req_queue_list, fn_res_queue_list)
                fn_req_queue.put(((), kwargs))
                out, e = fn_res_queue.get()
                if e is not None:
                    raise e
            finally:
                if fn_lock is not None:
                    fn_lock.release()

            output_info = []
            for key, _ in self.algorithm_config.service_output.items():
                output_info.append(out[key])
            return output_info if len(output_info) > 1 else output_info[0]

        inputs = []
        for _, info in self.algorithm_config.service_input.items():
            inputs.append(self.get_input_component(info['type'], info['describe']))
        outputs = []
        for _, info in self.algorithm_config.service_output.items():
            outputs.append(self.get_output_component(info['type'], info['describe']))

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

    def launch_self(self, gradio_port_con: Connection) -> None:
        ''' 启动自主编写的 Gradio 服务 '''
        # 校验自主实现的 Gradio 配置并附带将应用 import 入进程
        self.algorithm_config.verify_gradio_launch()
        threading.Thread(target=self.check_launched, args=(gradio_port_con,), daemon=True).start()
        with GradioPrint():
            self.algorithm_config.gradio_launch_fn()  # 启动 Gradio 服务

    async def handle(self, input_info: dict) -> dict:
        ''' 处理请求 '''
        self.logger.info('Begin to handle.')

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
            res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(url))
        if req_method == 'POST' and req_headers['Content-Type'] == 'application/json':
            res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(url, json=req_body, headers=req_headers))
        if req_method == 'POST' and req_headers['Content-Type'] != 'application/json':
            res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(url, data=req_body, headers=req_headers))

        if res is not None:
            res_status_code = res.status_code
            res_headers = dict(res.headers)
            res_body = res.content.hex()
            result = {
                'status_code': res_status_code,
                'headers': res_headers,
                'body': res_body,
            }
        else:
            result = {}

        self.logger.info('Complete.')
        return result

    async def handle_init(self) -> dict:
        ''' 处理 Gradio 初始化请求 '''
        self.init_logger.info('Begin to handle.')

        if not os.path.exists('./frontend'):
            gradio_path = '/'.join(gr.__file__.split('/')[:-1])
            gradio_frontend_path = os.path.join(gradio_path, 'templates/frontend')
            shutil.copytree(gradio_frontend_path, './frontend')
            os.remove('./frontend/index.html')  # 删除未渲染的 index.html

        async def upload_file(bashpath: str, subpath: str):
            ''' 递归上传文件夹里的文件 '''
            path = os.path.join(bashpath, subpath)
            if os.path.exists(os.path.join(path, '.DS_Store')):
                os.remove(os.path.join(path, '.DS_Store'))
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isdir(filepath):
                    await upload_file(bashpath, os.path.join(subpath, filename))
                else:
                    url = self.gradio_upload_url + '/' + subpath + '/' + filename  # type: ignore
                    file = open(filepath, 'r', encoding="UTF-8", errors='ignore')
                    res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(url, files={'file': file}, headers=login_instance.get_header()))
                    file.close()

        await upload_file('./frontend', '.')  # 上传文件夹里的文件

        if not os.path.exists('./frontend/index.html'):
            html_res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(
                f'http://{self.algorithm_config.gradio_server_host}:{self.algorithm_config.gradio_server_port}'))
            html_text = html_res.text
            html_file = open('./frontend/index.html', 'w+', encoding="UTF-8", errors='ignore')
            html_file.write(html_text)
            html_file.close()
        url = self.gradio_upload_url + '/index.html'  # type: ignore
        file = open('./frontend/index.html', 'r', encoding="UTF-8", errors='ignore')
        # 上传 index.html
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(url, files={'file': file}, headers=login_instance.get_header()))
        file.close()

        shutil.rmtree('./frontend')  # 删除已上传的文件夹

        self.init_logger.info('Complete.')
        return {}


class Service:
    ''' 算法提供方 Service '''

    def __init__(
        self,
        config_path: str,
        fetch_mode: str,
    ):
        self.algorithm_config = ConfigLoader(config_path)
        self.algorithm_info = Algoinfo(self.algorithm_config.name, self.algorithm_config.version)
        self.fetch_mode = fetch_mode

        self.login_headers = {}
        self.login_headers_timestamp = 0

        self.fn_service = FnService(self.algorithm_config)
        self.api_service = ApiService(self.algorithm_config, self.algorithm_info)
        self.gradio_service = GradioService(self.algorithm_config, self.algorithm_info)

        self.logger = Logger('Service', is_show_time=True)
        self.algo_logger = Logger(self.algorithm_info.upper_name, is_show_time=True)

    def launch(self,
               stdio_queue: multiprocessing.Queue,
               type: str,
               fn_lock_list: List[Lock],
               fn_req_queue_list: List[multiprocessing.Queue],
               fn_res_queue_list: List[multiprocessing.Queue],
               gradio_port_con: Optional[Connection] = None):
        try:
            QueueStdIO('stdout', stdio_queue)
            QueueStdIO('stderr', stdio_queue)
            if not self.login():
                raise Exception('Login failed.')
            if type == 'FN':
                self.fn_service.launch(fn_req_queue_list, fn_res_queue_list)
            elif type == 'SERVICE':
                if not gradio_port_con:
                    raise Exception('Argument \'gradio_port_con\' is None.')
                self.launch_service(fn_lock_list, fn_req_queue_list, fn_res_queue_list, gradio_port_con)
            elif type == 'GRADIO':
                if not gradio_port_con:
                    raise Exception('Argument \'gradio_port_con\' is None.')
                if self.algorithm_config.is_self_gradio_launch:
                    self.gradio_service.launch_self(gradio_port_con)
                else:
                    self.gradio_service.launch(fn_lock_list, fn_req_queue_list, fn_res_queue_list, gradio_port_con)
            else:
                raise Exception('Argument "type" is unaccessable.')
        except Exception as e:
            traceback.print_exc()
            self.algo_logger.error(f'Launch {type} error: {str(e)}')
            exit(1)

    def launch_service(self,
                       fn_lock_list: List[Lock],
                       fn_req_queue_list: List[multiprocessing.Queue],
                       fn_res_queue_list: List[multiprocessing.Queue],
                       gradio_port_con: Connection):
        # 从管道接受 Gradio 运行成功的端口
        gradio_port = int(gradio_port_con.recv())
        gradio_port_con.close()
        self.algorithm_config.gradio_server_port = gradio_port

        # 开始处理
        self.logger.info(f'Running in {self.fetch_mode} mode.')
        self.logger.info(f'Your algorithm site: {self.algorithm_info.algorithm_site}')
        self.logger.info('Start handling...')
        print('')

        parallel = {
            'max': self.algorithm_config.service_max_parallel,
            'curr': 0,
        }

        def is_parallel_full():
            return parallel['curr'] >= parallel['max']

        def add_parallel(is_full: bool = False):
            parallel['curr'] += 1 if not is_full else parallel['max']

        def minus_parallel(is_full: bool = False):
            parallel['curr'] -= 1 if not is_full else parallel['max']

        def get_rest_parallel():
            return parallel['max'] - parallel['curr']

        if self.fetch_mode == 'listen':
            def on_init():
                while is_parallel_full():
                    # 并行数达到上限，等待
                    time.sleep(config.wait_interval)
                return get_rest_parallel()

            def on_req(req_info: dict, loop: asyncio.AbstractEventLoop):
                # 处理请求
                try:
                    add_parallel(req_info['type'] == 'gradio_init')
                    future = asyncio.run_coroutine_threadsafe(self.handle(req_info, fn_lock_list,
                                                                          fn_req_queue_list, fn_res_queue_list), loop)
                    future.add_done_callback(lambda task: minus_parallel(
                        req_info['type'] == 'gradio_init'))  # type: ignore
                except Exception as e:
                    traceback.print_exc()
                    self.logger.error(f'Create handle task error: {str(e)}')

                while is_parallel_full():
                    # 并行数达到上限，等待
                    time.sleep(config.wait_interval)
                return get_rest_parallel()

            while True:
                # 断开会重连
                asyncio.run(self.ws_ask_data(on_init, on_req))
                time.sleep(config.wait_interval)

        elif self.fetch_mode == 'poll':
            async def start():
                loop = asyncio.get_event_loop()
                while True:
                    while is_parallel_full():
                        # 并行数达到上限，等待
                        await asyncio.sleep(config.wait_interval)

                    # 请求消息
                    try:
                        req_info = await self.ask_data()
                        if req_info is None:
                            await asyncio.sleep(config.wait_interval)
                            continue
                    except Exception as e:
                        traceback.print_exc()
                        self.logger.error(f'Ask data error: {str(e)}')
                        await asyncio.sleep(config.wait_interval)
                        continue

                    # 处理请求
                    try:
                        add_parallel(req_info['type'] == 'gradio_init')
                        future = loop.create_task(self.handle(req_info, fn_lock_list,
                                                              fn_req_queue_list, fn_res_queue_list))
                        future.add_done_callback(lambda task: minus_parallel(
                            req_info['type'] == 'gradio_init'))  # type: ignore
                        await asyncio.sleep(config.call_interval)
                    except Exception as e:
                        traceback.print_exc()
                        self.logger.error(f'Create handle task error: {str(e)}')
                        await asyncio.sleep(config.wait_interval)

            asyncio.run(start())

    async def ws_ask_data(self, on_init: Callable, on_req: Callable):
        try:
            loop = asyncio.get_event_loop()

            def on_message(ws: websocket.WebSocket, message):
                # websocket-client 限制消息体大小 64kb，需要注意
                result: dict = json.loads(message)
                if result.get('ack'):
                    rest_parallel = on_init()
                    ws.send(json.dumps({
                        'rest_parallel': rest_parallel,
                    }))
                else:
                    req_info = result['req_info']
                    rest_parallel = on_req(req_info, loop)
                    ws.send(json.dumps({
                        'rest_parallel': rest_parallel,
                    }))

            def on_open(ws: websocket.WebSocket):
                ws.send(json.dumps({
                    'algorithm_name': self.algorithm_info.name,
                    'algorithm_version': self.algorithm_info.version,
                }))

            ws = websocket.WebSocketApp(self.ws_ask_data_url,
                                        header=login_instance.get_header(),
                                        on_open=on_open,
                                        on_message=on_message)

            await loop.run_in_executor(None, ws.run_forever)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f'Websocket ask data error: {str(e)}')

    async def ask_data(self, id: Optional[str] = None) -> Optional[dict]:
        ask_for_data_resp = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(self.ask_data_url,
                                                                                                      params={
                                                                                                          'algorithm_name': self.algorithm_info.name,
                                                                                                          'algorithm_version': self.algorithm_info.version,
                                                                                                          **({'id': id} if id else {}),
                                                                                                      },
                                                                                                      headers=login_instance.get_header()))
        if ask_for_data_resp.status_code != 200 and ask_for_data_resp.status_code != 201:
            raise Exception(ask_for_data_resp.status_code, ask_for_data_resp.content.decode())
        ask_for_data_dict = ask_for_data_resp.json()
        if ask_for_data_dict['status'] == 201:
            # 没有新的请求信息
            return
        if ask_for_data_dict['status'] != 200:
            raise Exception('the response', ask_for_data_dict)
        req_data = ask_for_data_dict.get('data', {})
        if type(req_data) != dict:
            raise Exception('the property of \'data\' is not dict.')
        req_info = req_data.get('req_info', {})
        if type(req_info) != dict:
            raise Exception('the property of \'req_info\' is not dict.')
        return req_info

    async def handle(self,
                     req_info: dict,
                     fn_lock_list: List[Lock],
                     fn_req_queue_list: List[multiprocessing.Queue],
                     fn_res_queue_list: List[multiprocessing.Queue]):
        try:
            try:
                if type(req_info['data']) != dict:
                    req_id = req_info['id']
                    full_req_info = None
                    retry_times = 0
                    max_retry_times = 5
                    while not full_req_info:
                        if retry_times >= max_retry_times:
                            raise Exception(f'Algo req \'{req_id}\' is not found.')
                        try:
                            full_req_info = await self.ask_data(req_id)
                        except:
                            pass
                        finally:
                            retry_times += 1
                            await asyncio.sleep(config.wait_interval * retry_times)
                    req_info = full_req_info

                # 根据请求类型处理
                if req_info['type'] == 'api':
                    # 处理计算请求
                    result = await asyncio.get_event_loop().run_in_executor(None, lambda: self.api_service.handle(req_info['data'], fn_lock_list, fn_req_queue_list, fn_res_queue_list))
                elif req_info['type'] == 'gradio':
                    # 处理 Gradio 请求
                    result = await self.gradio_service.handle(req_info['data'])
                elif req_info['type'] == 'gradio_init':
                    # 处理 Gradio 初始化请求
                    result = await self.gradio_service.handle_init()
                else:
                    result = {}

                # 回传数据
                res_info = {
                    'id': req_info['id'],
                    'name': req_info['name'],
                    'version': req_info['version'],
                    'type': req_info['type'],
                    'status': 'success',
                    'owner': req_info['owner'],
                    'create_date': req_info['create_date'],
                    'result': result
                }
                return_ans_param = {
                    'res_info': res_info,
                    'algorithm_name': req_info['name'],
                    'algorithm_version': req_info['version']
                }
                return_ans_resp = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(self.return_ans_url,
                                                                                                             json=return_ans_param,
                                                                                                             headers=login_instance.get_header()))

                if return_ans_resp.status_code != 200 and return_ans_resp.status_code != 201 and return_ans_resp.json()['status'] != 200:
                    err_msg = "Service Result Return Error."
                    raise Exception(err_msg)
                else:
                    self.logger.info(f'Return ans success.')
            except Exception as e:
                traceback.print_exc()
                # 回传失败数据
                res_info = {
                    'id': req_info['id'],
                    'name': req_info['name'],
                    'version': req_info['version'],
                    'type': req_info['type'],
                    'status': 'error',
                    'owner': req_info['owner'],
                    'create_date': req_info['create_date'],
                    'result': {'err_msg': str(e)}
                }
                return_error_param = {
                    'res_info': res_info,
                    'algorithm_name': req_info['name'],
                    'algorithm_version': req_info['version']
                }
                await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(self.return_err_url,
                                                                                           json=return_error_param,
                                                                                           headers=login_instance.get_header()))
                self.logger.error(f'Return error ans success.')
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f'Handle error: {str(e)}')

    def login(self):
        if not login(secret=self.algorithm_config.secret, username=self.algorithm_config.username, password=self.algorithm_config.password, privilege='PROVIDER'):
            self.algo_logger.error(f'Login failed. Please check your secret or password.')
            return False
        return True

    def enroll(self):
        try:
            enroll(self.algorithm_config.name,
                   self.algorithm_config.version,
                   self.algorithm_config.service_input,
                   self.algorithm_config.service_output,
                   self.algorithm_config.description,
                   self.algorithm_config.scope,
                   self.algorithm_config.chinese_name,
                   self.algorithm_config.document,
                   self.algorithm_config.config_file_content)
            return True
        except Exception as e:
            self.algo_logger.error(f'Enroll failed: {str(e)}')
            return False

    def verify_config(self):
        try:
            file = verify_config(self.algorithm_config.name,
                                 self.algorithm_config.version,
                                 self.algorithm_config.service_input,
                                 self.algorithm_config.service_output)
            if file:
                dirpath = os.path.dirname(self.algorithm_config.config_path)
                filepath = os.path.join(dirpath, 'algospace-config-origin.py')
                with open(filepath, 'w') as f:
                    f.write(file)
                self.algo_logger.error(
                    f'Content of \'{self.algorithm_config.config_path}\' is not same as the config enrolled before. The original config file is regenerated at \'{filepath}\'. Please use the original file to start. Or if you have modified the algorithm, use a new \'version\' to start.')
                return False
            return True
        except Exception as e:
            self.algo_logger.error(f'Verify config failed: {str(e)}')
            return False

    def is_component_normal(self):
        while (True):
            res = is_component_normal(self.algorithm_config.name, self.algorithm_config.version)
            if res['is_component_normal']:
                self.ask_data_url = res['ask_data_url']
                self.ws_ask_data_url = res['ws_ask_data_url']
                self.return_ans_url = res['return_ans_url']
                self.return_err_url = res['return_err_url']
                self.gradio_service.gradio_upload_url = res['gradio_upload_url']
                break
            self.algo_logger.info(f'Waiting for components started...')
            time.sleep(5)

    def send_heartbeat(self):
        body = {
            'algorithm_name': self.algorithm_info.name,
            'algorithm_version': self.algorithm_info.version
        }
        requests.post(config.heartbeat_url, data=body, headers=login_instance.get_header())

    async def start(self):
        # 初始化状态
        self.algo_logger.info(f'Initializing...')
        if not self.login():
            return
        if not self.enroll():
            return
        if not self.verify_config():
            return
        self.is_component_normal()

        # 开启子进程
        stdio_queue = multiprocessing.Queue(maxsize=0)  # 子进程通过队列将标准 IO 重定向到父进程
        fn_lock_list = [multiprocessing.Lock() for _ in range(
            self.algorithm_config.service_max_parallel)]  # 模型函数的锁列表
        fn_req_queue_list = [multiprocessing.Queue(maxsize=0) for _ in range(
            self.algorithm_config.service_max_parallel)]  # 模型函数的请求队列列表
        fn_res_queue_list = [multiprocessing.Queue(maxsize=0) for _ in range(
            self.algorithm_config.service_max_parallel)]  # 模型函数的响应队列列表
        gradio_port_con1, gradio_port_con2 = multiprocessing.Pipe()  # 传递 Gradio 端口的管道

        def create_fn_process():
            fn_process = multiprocessing.Process(target=self.launch,
                                                 args=(stdio_queue,
                                                       'FN',
                                                       fn_lock_list,
                                                       fn_req_queue_list,
                                                       fn_res_queue_list),
                                                 daemon=True)
            fn_process.start()
            return fn_process

        def create_service_process():
            service_process = multiprocessing.Process(target=self.launch,
                                                      args=(stdio_queue,
                                                            'SERVICE',
                                                            fn_lock_list,
                                                            fn_req_queue_list,
                                                            fn_res_queue_list,
                                                            gradio_port_con2),
                                                      daemon=True)
            service_process.start()
            return service_process

        def create_gradio_process():
            gradio_process = multiprocessing.Process(target=self.launch,
                                                     args=(stdio_queue,
                                                           'GRADIO',
                                                           fn_lock_list,
                                                           fn_req_queue_list,
                                                           fn_res_queue_list,
                                                           gradio_port_con1),
                                                     daemon=True)
            gradio_process.start()
            return gradio_process

        def check_process_alive(process: multiprocessing.Process):
            is_alive = process.is_alive()
            if not is_alive:
                process.kill()
            return is_alive

        fn_process = create_fn_process()
        service_process = create_service_process()
        gradio_process = create_gradio_process()

        self.algo_logger.info(f'Waiting for service launched...')

        # 开启事件循环
        async def alive_task():
            nonlocal fn_process
            nonlocal service_process
            nonlocal gradio_process
            while True:
                await asyncio.sleep(1)
                if not check_process_alive(fn_process):
                    raise Exception('Fn process is not alive. Please check error log above.')
                if not check_process_alive(service_process):
                    raise Exception('Service process is not alive')
                if not check_process_alive(gradio_process):
                    raise Exception('Gradio process is not alive')

        async def heartbeat_task():
            times = 0
            while True:
                try:
                    await asyncio.sleep(1)
                    if times % 10 == 0:
                        # 每 10 秒发送心跳
                        await asyncio.get_running_loop().run_in_executor(None, self.send_heartbeat)
                        times = 0
                    times += 1
                except Exception as e:
                    traceback.print_exc()
                    self.algo_logger.error(f'Heartbeat error: {str(e)}')

        async def subprocess_stdio_task():
            queue_stdio_exec = QueueStdIOExec(stdio_queue)
            stdio_exec = queue_stdio_exec.exec
            stdio_exec_all = queue_stdio_exec.exec_all
            is_execed = True
            while True:
                try:
                    if not is_execed:
                        await asyncio.sleep(0.1)
                    is_execed = await asyncio.get_running_loop().run_in_executor(None, stdio_exec)
                except Exception as e:
                    traceback.print_exc()
                    self.algo_logger.error(f'Handle subprocess stdio error: {str(e)}')
                except asyncio.CancelledError:
                    stdio_exec_all()
                    raise

        # 当有任务抛出异常时，停止所有任务
        tasks = [alive_task(), heartbeat_task(), subprocess_stdio_task()]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        for task in pending:
            task.cancel()
        for task in done:
            task.result()


def run_service(config_path: str, fetch_mode: str = 'listen') -> None:
    loop = asyncio.get_event_loop()
    try:
        algospace_logger.info('Init.')
        service = Service(config_path, fetch_mode)
        loop.run_until_complete(service.start())
    except:
        traceback.print_exc()
    finally:
        algospace_logger.info('Exit.')
