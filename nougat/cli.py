import fire
import os
import sys
import time
import subprocess
import toml
from inspect import getmembers
from pathlib import Path
from nougat.app import Nougat
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NougatDebugMode(FileSystemEventHandler):

    def __init__(self, port=8000):
        self.app_process: subprocess.Popen = None
        self.port = port

    def start_server(self):
        os.system('clear')
        print('Nougat is working on develop mode')
        self.app_process = subprocess.Popen(['nougat', 'run', '--port', str(self.port), '--debug'])

    def stop_server(self):
        self.app_process.kill()

    def on_modified(self, event):
        name = Path(event.src_path).name
        if not name.startswith('.') and name not in ['__pycache__']:
            self.stop_server()
            self.start_server()


class Commands(object):

    def __init__(self):
        sys.path.append(os.getcwd())

    def run(self, port=8000, debug=False):

        config = toml.load('nougat.toml')
        project_module = __import__(config['general']['dir'])
        application_instance = None
        for item in getmembers(project_module):
            name, instance = item
            if isinstance(instance, Nougat):
                application_instance = instance
                break

        if not application_instance:
            print("can't not find Nougat instance")
        else:
            application_instance.run(port=port, debug=debug)

    def develop(self, port: int=None):

        config = toml.load('nougat.toml')
        try:
            config_port = config['develop']['port']
        except KeyError:
            config_port = None

        port = int(port or config_port or 8000)
        event_handler = NougatDebugMode(port=port)
        event_handler.start_server()
        observer = Observer()
        observer.schedule(event_handler, os.getcwd(), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            event_handler.stop_server()
            observer.stop()
        observer.join()


def main():
    fire.Fire(Commands)
