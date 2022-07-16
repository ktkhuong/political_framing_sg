from pywinauto.application import Application
from pywinauto import keyboard 
from time import sleep

class Terminal:
    def __init__(self, session) -> None:
        #gcloud compute scp --recurse 2019Q1.pkl machine01:/home/ecmm451
        self.app = Application().start(cmd_line=f'putty -load "{session}"')
        self.putty = self.app.PuTTY
        self.putty.wait('ready')
        sleep(1)

    def run(self, command):
        self.putty.type_keys(command)
        self.putty.type_keys("{ENTER}")
        sleep(1)