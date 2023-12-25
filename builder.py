import logging
import os
import shutil
import copy
from git.repo.base import Repo
import sys
import json
import subprocess
import time
import stat


class BuildException(Exception):
    pass


class BenchBuilder():
    def __init__(self):
        self.repo_path = "umisoft-19/core.git"
        self.git_branch = "bench_v2"
        self.start = time.time()
        self.task_start = time.time()

    def run(self):
        self.configure_logger()
        self.setup_environment()
        self.download_source()
        self.assets_checks_and_build()
        self.setup_server_env()
        self.setup_launcher_env()
        self.build_launcher()
        self.build_wheels()
        self.build_server()

    def log_job_start(self):
        self.task_start = time.time()

    def log_duration(self):
        duration = time.time() - self.task_start
        cumulative = time.time() - self.start
        self.logger.info("Task took: %ds cumulative time: %d s", duration, cumulative)

    def download_source(self):
        self.logger.info("[Step 2] Downloading source")
        self.log_job_start()
        if os.path.exists(self.src_dir) and list(os.scandir(self.src_dir)):
            self.logger.info("Source directory is not empty")
            return
        os.chdir(self.src_dir)
        Repo.clone_from(
            "https://github.com/" + self.repo_path, 
            ".",
            single_branch=True,
            depth=1,
            branch=self.git_branch)
        self.logger.info("Downloaded %s successfully", self.repo_path)
        self.log_duration()

    def configure_logger(self):
        log_file = "build.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        self.logger = logging.getLogger('build')
        self.logger.setLevel(logging.DEBUG)

        log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s ] %(message)s")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def setup_environment(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.dir, 'dist')
        self.temp_dir = os.path.join(self.dir, 'temp')
        self.src_dir = os.path.join(self.dir, 'temp', 'src')
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        # TODO keep artifacts for speed
        # if os.path.exists(self.temp_dir):
        #     shutil.rmtree(self.temp_dir)
        

        env = copy.deepcopy(os.environ)
        # env['PATH'] = ";".join([
        #     os.path.join(self.base_dir, 'installer'),
        #     os.path.join(self.base_dir, 'client'),
        # ]) + env["PATH"]
        # self.env = env

        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        if not os.path.exists(self.dist_dir):
            os.mkdir(self.dist_dir)        
        if not os.path.exists(self.src_dir):
            os.mkdir(self.src_dir)
        

    def assets_checks_and_build(self):
        self.logger.info("[Step 3] Checking react bundles")
        self.log_job_start()
        
        self.stats_file_path = os.path.join(self.src_dir, 
            'assets', 
            'webpack-stats.json')
        with open(self.stats_file_path, 'r') as stats_file:
            if json.load(stats_file).get("status", "") != "done":
                self.logger.critical("The webpack bundles are not ready")
                raise BuildException("There are errors in the webpack bundles")

        os.chdir(self.src_dir)

        self.logger.info("[Step 4] Making production build of react modules")
        os.chdir(os.path.join(self.src_dir, 'assets'))
        if not os.path.exists("node_modules"):
            self.logger.info("installing npm packages")

        print(os.getcwd())
        res = subprocess.run(['npm', 'install'], check=True, shell=True)
        if res.returncode != 0:
            self.logger.error('Failed to install node modules ')
            raise BuildException('Failed to build react bundles')

        res = subprocess.run(['webpack.cmd', '--config', 'webpack.prod.js'])
        if res.returncode != 0:
            self.logger.error('Failed to build react bundles')
            raise BuildException('Failed to build react bundles')

        os.chdir(self.temp_dir)
        self.log_duration()

    def setup_launcher_env(self):
        self.logger.info("[Step 6] setting up launcher env")
        self.log_job_start()
        os.chdir(self.temp_dir)
        if os.path.exists(('launcher_env')):
            return
        shutil.copytree(os.path.join('..', 'launcher'), './launcher')
        res = subprocess.run('python -m venv launcher_env'.split(' '))
        if res.returncode != 0:
            self.logger.error("could not create a virtual environment")

        res = subprocess.run(['launcher_env/Scripts/pip', 'install', '-r', 'launcher/requirements.txt'])
        if res.returncode != 0:
            self.logger.error("could not install requirements")

        self.log_duration() 

    def setup_server_env(self):
        self.logger.info("[Step 5] setting up server env")
        self.log_job_start()
        os.chdir(self.temp_dir)
        if os.path.exists(('env')):
            return
        res = subprocess.run('python -m venv env'.split(' '))
        if res.returncode != 0:
            self.logger.error("could not create a virtual environment")

        res = subprocess.run(['env/Scripts/pip', 'install', '-r', 'src/requirements.txt'])
        if res.returncode != 0:
            self.logger.error("could not install requirements")

        self.log_duration()

    def build_launcher(self):
        self.logger.info("[Step 7] building launcher")
        self.log_job_start()
        os.chdir(self.temp_dir)
        res = subprocess.run(['launcher_env/Scripts/pyinstaller', 'launcher/launcher.spec', '--clean'])
        if res.returncode != 0:
            self.logger.error("could not build the launcher")

        self.log_duration()

    def build_wheels(self):
        self.logger.info("[Step 8] building wheels")
        self.log_job_start()
        os.chdir(self.temp_dir)
        if os.path.exists('wheels'):
            return
        os.mkdir('wheels')
        with open('../wheel_names.txt', 'r') as wheels_file:
            for line in wheels_file:
                line = line.strip()
                if line:
                    res = subprocess.run(['pip', 'wheel', '--wheel-dir=./wheels/', line])
                    if res.returncode != 0:
                        self.logger.error("could not build the wheel %s", line)

        with open('../wheels.txt', 'w') as f:
            for file in os.listdir('wheels'):
                f.write(file + '\n')

        self.log_duration()


    def build_server(self):
        self.logger.info("[Step 9] building server")
        self.log_job_start()
        os.chdir(self.temp_dir)
        if not os.path.exists('config_builder.py'):
            shutil.copyfile('../config_builder.py', 'config_builder.py')

        res = subprocess.run(['python', 'config_builder.py'])
        if res.returncode != 0:
            self.logger.error("could not create nsist config")

        if not os.path.exists('src/__init__.py'):
            with open('src/__init__.py', 'w') as f:
                f.write('# Bench Business Tools')

        res = subprocess.run(['pynsist', 'installer.cfg'])
        if res.returncode != 0:
            self.logger.error("could not build the server with pynsist")

        self.log_duration()

    def package_app(self):
        self.logger.info("[Step 10] packaging the app")
        self.log_job_start()
        os.chdir(self.temp_dir)
        self.log_duration()



if __name__ == "__main__":
    builder = BenchBuilder()
    builder.run()
