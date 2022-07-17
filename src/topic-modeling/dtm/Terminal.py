from time import sleep
import threading

lock = threading.Lock()

class Terminal:
    def __init__(self, session) -> None:
        self.app = Application().start(cmd_line=f'putty -load "{session}"')
        self.putty = self.app.PuTTY
        self.putty.wait('ready')
        sleep(1)

    def send_command(self, cmd, wait=0):
        lock.acquire()
        cmd = cmd.replace(" ", "{SPACE}")
        self.run(cmd)
        if wait > 0:
            sleep(wait)
        lock.release()

    def run(self, command):
        self.putty.type_keys(command)
        self.putty.type_keys("{ENTER}")
        sleep(1)

    def exit(self):
        self.send_command("exit")