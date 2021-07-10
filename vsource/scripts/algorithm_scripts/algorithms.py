import os
import inspect
import traceback

class AlgorithmContainerConfigParser:
    def __init__(self, config):
        self.cur_dir = os.path.dirname(__file__)

        self.logs = []
        self.pre_check(config)

    def pre_check(self, config):
        try:
            self.service_dir       = config['service-dir']
            self.service_filename  = config['service-filename']
            if str(self.service_filename).endswith('.py'):
                self.service_filename = self.service_filename[:-3]
            self.service_interface = config['service-interface']
            self.algorithm_name    = config['algorithm-name']
            self.requirements      = config['requirements']
            self.pre_command       = config['pre-command']
            self.input_params      = config['input-params']
            self.output_params     = config['output-params']
            assert os.path.exists(self.service_dir)
        except AssertionError:
            err_msg = traceback.format_exc()
            traceback.print_exc()
            self.logs.append('[Step 0 Error, Service Directory not exists]: ' + err_msg)
        except KeyError:
            err_msg = traceback.format_exc()
            traceback.print_exc()
            self.logs.append('[Step 0 Error, KeyError, invalid config]: ' + err_msg)

    # 第一步，生成requirements.txt
    def gen_requirements_txt(self):
        try:
            with open(os.path.join(self.service_dir, 'vsource_requirements.txt'), 'w') as f:
                for each_requirement in self.requirements:
                    f.write(each_requirement)
                    f.write('\n')
                f.write("redis\n")
                f.write('kafka-python\n')
            self.logs.append('[Step 1/6] Requirements has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 2 Error, Requirements Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第二步，生成dockerfile
    def gen_dockerfile(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-dockerfile.template'), 'r') as f:
                templates = f.read()

            pre_command_lines = ""
            for each_command in self.pre_command:
                pre_command_lines += ("RUN " + each_command + "\n")
            requirements_lines = "RUN pip --timeout=1000000 install -r vsource_requirements.txt \n"
            templates = templates.format(pre_command_lines, requirements_lines)

            with open(os.path.join(self.service_dir, 'vsource_dockerfile'), 'w') as f:
                f.write(templates)
            self.logs.append('[Step 2/6] Dockerfile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 2 Error, Dockerfile Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第三步，生成vsource_configs.py
    def gen_configs(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-configs.template'), 'r') as f:
                templates = f.read()

            with open(os.path.join(self.service_dir, 'vsource_configs.py'), 'w') as f:
                f.write(templates)
            self.logs.append('[Step 3/6] Configfile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 3 Error, ConfigFile Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第四步，service.py
    def gen_service(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-service.template'), 'r') as f:
                templates = f.read()
            import_lines = 'import {}'.format(self.service_filename)
            param_init_lines = ""
            for each_input_param_name in self.input_params:
                param_init_lines += ('            {} = info_dict[\'{}\']\n'.format(each_input_param_name, each_input_param_name))
            function_lines =  "            out = {}.{}(".format(self.service_filename, self.service_interface)
            for each_input_param_name in list(self.input_params.keys())[:-1]:
                function_lines += (each_input_param_name + ', ')
            function_lines += (list(self.input_params.keys())[-1] + ")\n")
            output_lines = "            return out\n"
            templates = templates.format(import_lines, param_init_lines + function_lines + output_lines)
            with open(os.path.join(self.service_dir, 'vsource_service.py'), 'w') as f:
                f.write(templates)
            self.logs.append('[Step 4/6] Servicefile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 4 Error, Servicefile Generated Failed]: ' + err_msg)
            traceback.print_exc()


    # 第五步，deployment-compose.yaml
    def gen_deployment_compose(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-deploy-compose.template'), 'r') as f:
                templates = f.read()
            templates = templates.format(
                self.algorithm_name, self.algorithm_name, self.algorithm_name
            )
            with open(os.path.join(self.service_dir, 'vsource_deploy_compose.yaml'), 'w') as f:
                f.write(templates)
            self.logs.append('[Step 5/6] Deployment compose file has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 5 Error, Deployment compose file Generated Failed]: ' + err_msg)
            traceback.print_exc()

    def gen_control_script(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-start.template'), 'r') as f:
                templates = f.read()
            with open(os.path.join(self.service_dir, 'vsource_deploy_compose.yaml'), 'w') as f:
                pass
            templates = templates.format(
                self.algorithm_name, self.algorithm_name, self.algorithm_name
            )
            with open(os.path.join(self.service_dir, 'vsource_deploy_compose.yaml'), 'w') as f:
                f.write(templates)
            self.logs.append('[Step 5/6] Deployment compose file has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logs.append('[Step 5 Error, Deployment compose file Generated Failed]: ' + err_msg)
            traceback.print_exc()

    def generate(self):
        self.gen_requirements_txt()
        self.gen_dockerfile()
        self.gen_configs()
        self.gen_service()
        # self.gen_deployment_kube()
        self.gen_deployment_compose()

def parse_algorithm(config):
    a = AlgorithmContainerConfigParser(config)
    a.generate()

if __name__ == '__main__':
    config = {
        'algorithm-name': 'new_algorithm',
        'version': '1.0.1',
        'author': 'xcy',
        'service-dir': '/Users/ecohnoch/Desktop/VSOURCE_PLATFORM/algorithm_api/new_algorithm',
        'service-filename': 'test_function.py',
        'service-interface': 'random_number',
        'requirements': [
            'numpy==1.19.0',
            'opencv-python'
        ],
        'pre-command': [
            'apt install -y libgl1-mesa-glx'
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
            'result': 'calculated results, as a random number'
        }
    }

    a = AlgorithmContainerConfigParser(config)
    a.generate()
