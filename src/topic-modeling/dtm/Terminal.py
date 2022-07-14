from pywinauto.application import Application
from pywinauto import keyboard 
from time import sleep

class Terminal:
    def __init__(self, host) -> None:
        self.app = Application().start(cmd_line=f'putty -ssh tk402@{host}.ex.ac.uk -pw Ukw634uY0b')
        self.putty = self.app.PuTTY
        self.putty.wait('ready')
        sleep(1)

    def run(self, command):
        self.putty.type_keys(command)
        self.putty.type_keys("{ENTER}")
        sleep(1)