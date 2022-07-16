import subprocess
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE
import sys
import os
from time import sleep
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE
import threading
from Terminal import Terminal

lock = threading.Lock()

def send_command(terminal, cmd):
    lock.acquire()
    cmd = cmd.replace(" ", "{SPACE}")
    terminal.run(cmd)
    lock.release()

def spawn(session):
    terminal = Terminal(session)
    #send_command(terminal, "cd ecmm451")
    #send_command(terminal, "rm -r ecmm451")
    #send_command(terminal, f"mkdir {i}")
    sleep(5)
    send_command(terminal, "exit")

def main():
    #env = os.environ.copy()
    threads = []
    for session in ["blue01"]:#, "blue02", "blue03", "blue04", "blue05", "blue06"]:
        t = threading.Thread(target=spawn, args=(session,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

    print("finish")

if __name__ == "__main__":
    main()

