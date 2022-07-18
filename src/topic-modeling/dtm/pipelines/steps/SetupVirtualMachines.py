from time import sleep
from sklearn.base import BaseEstimator, TransformerMixin
import os, subprocess, logging
import threading
from models.TimeWindow import TimeWindow

class SetupVirtualMachines(BaseEstimator, TransformerMixin):
    PRIVATE_KEY = "ssh/sgparl_private.ppk"

    def __init__(self, machines):
        self.machines = machines

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        threads = []
        for host, _ in self.machines:
            t = threading.Thread(target=self.setup, args=(host,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        return X

    def setup(self, host):
        logger = logging.getLogger(__name__)
        logger.message(f"{host} setup ...")
        commands = [
            "sudo rm -rf *",
            "git clone -b cloud --single-branch https://github.com/ktkhuong/sgparl.git cloud",
            "sudo chmod 777 cloud/data",
        ]
        batch = ";".join(commands)
        p = subprocess.Popen(f'plink -i {self.PRIVATE_KEY} -batch sgparl@{host} "{batch}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p.wait()