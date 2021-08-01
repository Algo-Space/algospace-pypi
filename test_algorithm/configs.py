import vsource

if __name__ == '__main__':
    algorithm_config = {
        # 算法定义的名字
        'algorithm-name': 'random_number',
        # 算法的版本号
        'version': '1.0.2',
        # 算法的作者
        'author': 'xcy',
        # 算法工程文件夹的路径
        'service-dir': './',
        # 算法函数的所处的Python文件名
        'service-filename': 'random_number.py',
        # 算法的函数的标识符
        'service-interface': 'random_number',
        # 算法所依赖的Python库及版本
        'requirements': [
            'numpy==1.19.0',
        ],
        # 算法所依赖的非Python的软件，以Ubuntu的安装方式为标准
        'pre-command': [
            # 'apt install -y libgl1-mesa-glx'
        ],
        'input-params': {
            'lower': {
                'type': 'float',
                'describe': 'lower limit for thin function'
            },
            'upper': {
                'type': 'float',
                'describe': 'upper limit for thin function'
            },
        },
        'output-params': {
            'result': {
                'type': 'float',
                'describe': 'calculated  result'
            }
        }
    }

    vsource.parse_algorithm(algorithm_config)