import os
import traceback

class AlgorithmContainerConfigParser:
    def __init__(self, config):
        self.cur_dir = os.path.dirname(__file__)

        self.logs = []
        self.pre_check(config)

    def pre_check(self, config):
        try:
            self.login_username    = config['login_username']
            self.login_password    = config['login_password']
            self.service_dir       = config['service-dir']
            self.service_filename  = config['service-filename']
            if str(self.service_filename).endswith('.py'):
                self.service_filename = self.service_filename[:-3]
            self.service_interface = config['service-interface']
            self.algorithm_name    = config['algorithm-name']
            self.algorithm_version = config['version']
            self.algorithm_port    = config['port']
            self.requirements      = config['requirements']
            self.pre_command       = config['pre-command']
            self.input_params      = config['input-params']
            self.output_params     = config['output-params']
            assert os.path.exists(self.service_dir)
        except AssertionError:
            err_msg = traceback.format_exc()
            traceback.print_exc()
            print('[Step 0 Error, Service Directory not exists]: ' + err_msg)
        except KeyError:
            err_msg = traceback.format_exc()
            traceback.print_exc()
            print('[Step 0 Error, KeyError, invalid config]: ' + err_msg)

    # 第一步，生成requirements.txt
    def gen_requirements_txt(self):
        try:
            with open(os.path.join(self.service_dir, 'vsource_requirements.txt'), 'w') as f:
                for each_requirement in self.requirements:
                    if 'torch==' in each_requirement.replace(' ', ''):
                        # 如果是Pytorch，要从官网下载可支持版本，否则会出问题，查看Dockerfile那里
                        f.write('--find-links https://download.pytorch.org/whl/torch_stable.html\n')
                        f.write(each_requirement + '\n')
                    elif 'torchvision' in each_requirement:
                        f.write('--find-links https://download.pytorch.org/whl/torch_stable.html\n')
                        f.write(each_requirement + '\n')
                    else:
                        f.write(each_requirement + '\n')
                        f.write('\n')
                f.write('requests\n')
                f.write('vsource\n')
            print('[Step 1/6] Requirements has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 2 Error, Requirements Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第二步，生成dockerfile
    def gen_dockerfile(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-dockerfile.template'), 'r') as f:
                templates = f.read()

            pre_command_lines = ""
            for each_command in self.pre_command:
                pre_command_lines += ("RUN " + each_command + "\n")

            templates = templates.replace("{PRE_PROCESS}", pre_command_lines)

            requirements_lines = "RUN pip --timeout=1000000 install -r vsource_requirements.txt \n"

            templates = templates.replace("{PIP_PROCESS}", requirements_lines)

            with open(os.path.join(self.service_dir, 'vsource_dockerfile'), 'w') as f:
                f.write(templates)
            print('[Step 2/6] Dockerfile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 2 Error, Dockerfile Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第三步，生成vsource_configs.py
    def gen_configs(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-configs.template'), 'r') as f:
                templates = f.read()

            with open(os.path.join(self.service_dir, 'vsource_configs.py'), 'w') as f:
                f.write(templates)
            print('[Step 3/6] Configfile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 3 Error, ConfigFile Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第四步，service.py
    def gen_service(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-service.template'), 'r') as f:
                templates = f.read()
            import_lines = 'import {}'.format(self.service_filename)

            templates = templates.replace("{IMPORT_LINES}", import_lines)

            param_init_lines = ""
            for each_input_param_name in self.input_params:
                param_init_lines += ('            {} = info_dict[\'{}\']\n'.format(each_input_param_name, each_input_param_name))
                if self.input_params[each_input_param_name]['type'] == 'path':
                    param_init_lines += ('            {} = self.read_file({})\n'.format(each_input_param_name, each_input_param_name))
                elif self.input_params[each_input_param_name]['type'] == 'float':
                    param_init_lines += ('            {} = float({})\n'.format(each_input_param_name, each_input_param_name))
                elif self.input_params[each_input_param_name]['type'] == 'int':
                    param_init_lines += ('            {} = int({})\n'.format(each_input_param_name, each_input_param_name))
                elif self.input_params[each_input_param_name]['type'] == 'str':
                    param_init_lines += ('            {} = str({})\n'.format(each_input_param_name, each_input_param_name))
                else:
                    param_init_lines += ('            {} = {}({})\n'.format(each_input_param_name, self.input_params[each_input_param_name]['type'],  each_input_param_name))

            function_lines =  "            out = {}.{}(".format(self.service_filename, self.service_interface)
            if len(list(self.input_params.keys())) == 0:
                function_lines += ")\n"
            else:
                for each_input_param_name in list(self.input_params.keys())[:-1]:
                    function_lines += (each_input_param_name + ', ')
                function_lines += (list(self.input_params.keys())[-1] + ")\n")

            for each_output_param in self.output_params:
                if self.output_params[each_output_param]['type'] == 'path':
                    function_lines += '            {} = self.write_file({})\n'.format(each_output_param, 'out[\'{}\']'.format(each_output_param))
                    function_lines += '            out[\'{}\'] = {}\n'.format(each_output_param, each_output_param)
            output_lines = "            return out\n"

            templates = templates.replace('{FUNCTION_LINES}', param_init_lines + function_lines + output_lines)

            lower_name = self.algorithm_name.replace('-', '_').replace('.', '_').lower()
            lower_version = self.algorithm_version.replace('-', '_').replace('.', '_').lower()
            templates = templates.replace('{ALGORITHM_NAME}', lower_name)
            templates = templates.replace('{ALGORITHM_VERSION}', lower_version)
            with open(os.path.join(self.service_dir, 'vsource_service.py'), 'w') as f:
                f.write(templates)
            print('[Step 4/6] Servicefile has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 4 Error, Servicefile Generated Failed]: ' + err_msg)
            traceback.print_exc()


    # 第五步，deployment-compose.yaml
    def gen_deployment_compose(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-deploy-compose.template'), 'r') as f:
                templates = f.read()

                # {ALGORITHM_FULL_NAME}:
                # image: 120.26
                # .143
                # .61: 10020 / service / {ALGORITHM_NAME}:{ALGORITHM_VERSION}
                # environment:
                # LOGIN_USERNAME: {LOGIN_USERNAME}
                # LOGIN_PASSWORD: {LOGIN_PASSWORD}
                # STORAGE_HOST: http: // 120.26
                # .143
                # .61: 13402
                # ALGORITHM_NAME: {ALGORITHM_NAME}
                # ALGORITHM_VERSION: {ALGORITHM_VERSION}
                # ALGORITHM_PORT: {ALGORITHM_PORT}

            lower_name = self.algorithm_name.replace('_', '-').lower()
            templates = templates.replace("{ALGORITHM_FULL_NAME}", lower_name)
            templates = templates.replace("{ALGORITHM_NAME}", self.algorithm_name.replace('_', '-').lower())
            templates = templates.replace("{ALGORITHM_VERSION}", self.algorithm_version)
            templates = templates.replace("{ALGORITHM_PORT}",  self.algorithm_port)
            templates = templates.replace("{LOGIN_USERNAME}", self.login_username)
            templates = templates.replace("{LOGIN_PASSWORD}", self.login_password)

            with open(os.path.join(self.service_dir, 'vsource_deploy_compose.yaml'), 'w') as f:
                f.write(templates)
            print('[Step 5/6] Deployment compose file has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 5 Error, Deployment compose file Generated Failed]: ' + err_msg)
            traceback.print_exc()

    # 第六步，control文件生成
    def gen_control_script(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-start.template'), 'r') as f:
                templates = f.read()
            with open(os.path.join(self.service_dir, 'vsource_start.sh'), 'w') as f:
                lower_name = self.algorithm_name.replace('_', '-').lower()
                templates = templates.format(lower_name, self.algorithm_version)
                f.write(templates)

            with open(os.path.join(self.cur_dir, 'algorithm-stop.template'), 'r') as f:
                templates = f.read()
            with open(os.path.join(self.service_dir, 'vsource_stop.sh'), 'w') as f:
                f.write(templates)

            with open(os.path.join(self.cur_dir, 'algorithm-logs.template'), 'r') as f:
                templates = f.read()
            with open(os.path.join(self.service_dir, 'vsource_logs.sh'), 'w') as f:
                f.write(templates)

            print('[Step 6/6] Deployment control file has been successfully generated!')
        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step 6 Error, Deployment compose file Generated Failed]: ' + err_msg)
            traceback.print_exc()

    def generate_local_start_script(self):
        try:
            with open(os.path.join(self.cur_dir, 'algorithm-local-start.template'), 'r') as f:
                templates = f.read()

            templates = templates.replace("{ALGORITHM_NAME}", self.algorithm_name)
            templates = templates.replace("{ALGORITHM_VERSION}", self.algorithm_version)
            templates = templates.replace("{ALGORITHM_PORT}", self.algorithm_port)
            templates = templates.replace("{LOGIN_USERNAME}", self.login_username)
            templates = templates.replace("{LOGIN_PASSWORD}", self.login_password)

            with open(os.path.join(self.service_dir, 'vsource_local_start.sh'), 'w') as f:
                f.write(templates)
            print('[Step Local] Local start script has been successfully generated!')

        except Exception as e:
            err_msg = traceback.format_exc()
            print('[Step Local Error, Local start script file Generated Failed]: ' + err_msg)
            traceback.print_exc()

    def generate(self):
        self.gen_requirements_txt()
        self.gen_dockerfile()
        self.gen_configs()
        self.gen_service()
        self.gen_deployment_compose()
        self.gen_control_script()

        self.generate_local_start_script()

def parse_algorithm(config):
    a = AlgorithmContainerConfigParser(config)
    a.generate()

if __name__ == '__main__':
    pass