#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Description: 
@Author: Ecohnoch(xcy)
@Date: 2022-10-06 12:30:47
@LastEditors: Kermit
@LastEditTime: 2022-10-23 12:27:31
'''

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
    lower_name = full_name.replace('-', '_').replace('.',  '_').lower()
    input_params = config['input-params']
    output_dir = config['output_dir']

    templates = templates.replace('{algorithm-name}', name_lower)
    templates = templates.replace('{algorithm-version}', version_lower)
    templates = templates.replace('{full-algorithm-api-name}', full_name_lower)
    templates = templates.replace('{full-algorithm-api-path}', lower_name)
    templates = templates.replace('{input-params}', json.dumps(list(input_params.keys())))
    templates = templates.replace('{full-algorithm-collector-name}', full_name_lower+'-collector')
    templates = templates.replace('{full-algorithm-request-db-name}', full_name_lower + '-request-db')

    # deployment_dir = os.path.join(os.path.dirname(os.path.dirname(dir_path)), 'deployment', 'algorithm-api')
    output_path = os.path.join(output_dir, full_name_lower +  '.yaml')
    with open(output_path, 'w') as f:
        f.write(templates)
        print('Successfully generated: ', output_path)