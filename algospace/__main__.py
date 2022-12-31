#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: AlgoSpace 脚本入口
@Author: Kermit
@Date: 2022-11-05 16:46:46
@LastEditors: Kermit
@LastEditTime: 2022-12-31 12:57:49
'''

from argparse import ArgumentParser


class ArgNamespace:
    command = 'command'
    version = 'version'
    config_path = 'config_path'
    generate_type = 'generate_type'
    generate_debian_mirror = 'generate_debian_mirror'
    generate_use_buildkit_debian_cache = 'generate_use_buildkit_debian_cache'
    generate_use_buildkit_pip_cache = 'generate_use_buildkit_pip_cache'
    cloud_deploy_reset = 'cloud_deploy_reset'


def run():
    parser = ArgumentParser('algospace', description='AlgoSpace 远程算法调用平台')
    subparsers = parser.add_subparsers(dest=ArgNamespace.command)  # ArgNamespace.command

    init_parser = subparsers.add_parser('init', description='初始化算法服务配置', help='初始化算法服务配置')
    start_parser = subparsers.add_parser('start', description='启动算法服务', help='启动算法服务')
    generate_parser = subparsers.add_parser('generate', description='生成容器配置', help='生成容器配置')
    enroll_parser = subparsers.add_parser('enroll', description='注册算法服务', help='注册算法服务')
    cloud_deploy_parser = subparsers.add_parser('cloud:deploy', description='部署云端托管算法', help='部署云端托管算法')
    cloud_log_parser = subparsers.add_parser('cloud:log', description='查看云端托管算法日志', help='查看云端托管算法日志')

    # 主命令参数
    parser.add_argument('-v',
                        '--version',
                        dest=ArgNamespace.version,
                        action='store_true',
                        help='显示版本信息')
    # start 命令参数
    start_parser.add_argument('-c',
                              '--config',
                              dest=ArgNamespace.config_path,
                              metavar='<path>',
                              type=str,
                              required=False,
                              default='algospace-config.py',
                              help='algospace-config.py 配置文件路径')
    # generate 命令参数
    generate_parser.add_argument('-c',
                                 '--config',
                                 dest=ArgNamespace.config_path,
                                 metavar='<path>',
                                 type=str,
                                 required=False,
                                 default='algospace-config.py',
                                 help='algospace-config.py 配置文件路径')
    generate_parser.add_argument('-d',
                                 '--debian-mirror',
                                 dest=ArgNamespace.generate_debian_mirror,
                                 metavar='<163,aliyun,ustc,tsinghua>',
                                 choices=['163', 'aliyun', 'ustc', 'tsinghua'],
                                 help='更改 Debian 镜像源')
    generate_parser.add_argument('--buildkit-debian-cache',
                                 dest=ArgNamespace.generate_use_buildkit_debian_cache,
                                 action='store_true',
                                 help='使用 BuildKit 缓存 Debian apt packages')
    generate_parser.add_argument('--buildkit-pip-cache',
                                 dest=ArgNamespace.generate_use_buildkit_pip_cache,
                                 action='store_true',
                                 help='使用 BuildKit 缓存 pip packages')
    # enroll 命令参数
    enroll_parser.add_argument('-c',
                               '--config',
                               dest=ArgNamespace.config_path,
                               metavar='<path>',
                               type=str,
                               required=False,
                               default='algospace-config.py',
                               help='algospace-config.py 配置文件路径')
    # cloud:deploy 命令参数
    cloud_deploy_parser.add_argument('-c',
                                     '--config',
                                     dest=ArgNamespace.config_path,
                                     metavar='<path>',
                                     type=str,
                                     required=False,
                                     default='algospace-config.py',
                                     help='algospace-config.py 配置文件路径')
    cloud_deploy_parser.add_argument('-r',
                                     '--reset',
                                     dest=ArgNamespace.cloud_deploy_reset,
                                     action='store_true',
                                     help='重新构建镜像，不使用已构建的镜像')
    # cloud:log 命令参数
    cloud_log_parser.add_argument('-c',
                                  '--config',
                                  dest=ArgNamespace.config_path,
                                  metavar='<path>',
                                  type=str,
                                  required=False,
                                  default='algospace-config.py',
                                  help='algospace-config.py 配置文件路径')

    args = ArgNamespace()
    parser.parse_args(namespace=args)

    if args.command is None or args.command == 'command':
        if args.version is True:
            from algospace import __version__
            print('AlgoSpace', __version__)
        else:
            parser.print_help()

    elif args.command == 'init':
        from algospace.provider.config_generator import generate_config
        generate_config()

    elif args.command == 'start':
        from algospace.provider.service import run_service
        run_service(args.config_path)

    elif args.command == 'generate':
        from algospace.provider.docker_generator import generate_docker_config
        generate_docker_config(args.config_path,
                               args.generate_debian_mirror,
                               args.generate_use_buildkit_debian_cache is True,
                               args.generate_use_buildkit_pip_cache is True)

    elif args.command == 'enroll':
        from algospace.provider.enroll import enroll_from_config
        enroll_from_config(args.config_path)

    elif args.command == 'cloud:deploy':
        from algospace.provider.cloud import run_cloud_deploy
        run_cloud_deploy(args.config_path, args.cloud_deploy_reset is True)

    elif args.command == 'cloud:log':
        from algospace.provider.cloud import show_running_log
        show_running_log(args.config_path)

    else:
        raise Exception(f'CommandError: \'{args.command}\' is an invalid command')


if __name__ == '__main__':
    run()
