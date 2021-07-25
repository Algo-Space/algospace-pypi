# -*- coding: utf-8 -*-
# @Author   : Ecohnoch(xcy)
# @File     : __init__.py.py
# @Function : TODO

import os
import json

def enroll(config):
    dir_path = os.path.dirname(__file__)
    template_path = os.path.join(dir_path,  'deployment.yaml.template')
    with open(template_path, 'r') as f:
        templates = f.read()
    algorithm_name = config['algorithm-name']
    algorithm_version = config['version']
    name_lower = algorithm_name.replace('_', '-').replace('.', '-').lower()
    version_lower = algorithm_version.replace('_', '-').replace('.', '-').lower()
    full_name = algorithm_name + '_' + algorithm_version
    full_name_lower = full_name.replace('_', '-').replace('.', '-').lower()
    algorithm_port = config['service-port']
    node_name = config['node-name']
    input_params = config['input-params']
    output_dir = config['output_dir']

    templates = templates.replace('{service-port}', str(algorithm_port))
    templates = templates.replace('{algorithm-name}', name_lower)
    templates = templates.replace('{algorithm-version}', version_lower)
    templates = templates.replace('{full-algorithm-api-name}', full_name_lower)
    templates = templates.replace('{input-params}', json.dumps(list(input_params.keys())))
    templates = templates.replace('{full-algorithm-collector-name}', full_name_lower+'-collector')
    templates = templates.replace('{full-algorithm-request-db-name}', full_name_lower + '-request-db')
    templates = templates.replace('{node-name}', node_name)

    # deployment_dir = os.path.join(os.path.dirname(os.path.dirname(dir_path)), 'deployment', 'algorithm-api')
    output_path = os.path.join(output_dir, full_name_lower +  '.yaml')
    with open(output_path, 'w') as f:
        f.write(templates)
        print('Successfully generated: ', output_path)