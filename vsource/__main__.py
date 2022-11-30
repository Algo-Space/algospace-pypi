#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: VSource 脚本入口
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2022-11-11 16:50:19
'''

from argparse import ArgumentParser


class ArgNamespace:
    command = 'command'
    config_path = 'config_path'
    enroll_remote = 'enroll_remote'
    generate_type = 'generate_type'


def run():
    parser = ArgumentParser('vsource', description='vsource 远程算法调用平台')
    subparsers = parser.add_subparsers(dest=ArgNamespace.command)  # ArgNamespace.command

    init_parser = subparsers.add_parser('init', description='初始化算法服务配置', help='初始化算法服务配置')
    start_parser = subparsers.add_parser('start', description='启动算法服务', help='启动算法服务')
    generate_parser = subparsers.add_parser('generate', description='生成容器配置', help='生成容器配置')
    enroll_parser = subparsers.add_parser('enroll', description='注册算法服务', help='注册算法服务')

    # start 命令参数
    start_parser.add_argument('-c', '--config', dest=ArgNamespace.config_path, metavar='<path>', type=str, required=False,
                              default='vsource-config.py', help='vsource-config.py 配置文件路径')  # ArgNamespace.config_path
    # generate 命令参数
    generate_parser.add_argument('-c', '--config', dest=ArgNamespace.config_path, metavar='<path>', type=str, required=False,
                                 default='vsource-config.py', help='vsource-config.py 配置文件路径')  # ArgNamespace.config_path
    # enroll 命令参数
    enroll_parser.add_argument('-c', '--config', dest=ArgNamespace.config_path, metavar='<path>', type=str, required=False,
                               default='vsource-config.py', help='vsource-config.py 配置文件路径')  # ArgNamespace.config_path
    enroll_parser.add_argument('-r', '--remote', dest=ArgNamespace.enroll_remote, required=False,
                               action='store_true', default=False, help='远程部署')  # ArgNamespace.config_path

    args = ArgNamespace()
    parser.parse_args(namespace=args)

    if args.command is None or args.command == 'command':
        parser.print_help()
    elif args.command == 'init':
        from vsource.provider.config_generator import generate_config
        generate_config()
    elif args.command == 'start':
        from vsource.provider.service import run_service
        run_service(args.config_path)
    elif args.command == 'generate':
        from vsource.provider.docker_generator import generate_docker_config
        generate_docker_config(args.config_path)
    elif args.command == 'enroll':
        from vsource.provider.enroll import enroll_from_config
        if not args.enroll_remote:
            enroll_from_config(args.config_path)
        else:
            print('Enrolling remotely will come soon.')
    else:
        raise Exception(f'CommandError: \'{args.command}\' is an invalid command')


if __name__ == '__main__':
    run()
