from time import sleep
from sklearn.base import BaseEstimator, TransformerMixin
import os, subprocess, logging
import threading
from models.TimeWindow import TimeWindow

class PreprocessDataset(BaseEstimator, TransformerMixin):
    PRIVATE_KEY = "ssh/sgparl_private.ppk"
    N_PARLIMENTS = 14

    def __init__(self, machines, dataset_url):
        self.machines = machines
        self.dataset_url = dataset_url

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        # preprocess
        threads = []
        for i, machine in enumerate(self.machines):
            host, _ = machine
            if i+1 <= self.N_PARLIMENTS:
                t = threading.Thread(target=self.preprocess, args=(host,i+1))
                t.start()
                threads.append(t)
        for t in threads:
            t.join()
        # download
        for i, machine in enumerate(self.machines):
            host, zone = machine
            if i+1 <= self.N_PARLIMENTS:
                p = subprocess.Popen(f"gcloud compute scp --recurse --zone={zone} machine{str(i+1).zfill(2)}:/home/sgparl/cloud/out/* in", shell=True)
                p.wait()
        
        return X

    def preprocess(self, host, parl_num):
        logger = logging.getLogger(__name__)
        logger.message(f"{host} preprocessing ...")
        commands = [
            f"sudo wget -P /home/sgparl/cloud {self.dataset_url}",
            "sudo unzip cloud/parliament.zip -d cloud/dataset",
            "cd cloud",
            "python3 -m venv env",
            "source env/bin/activate",
            "pip install -r requirements.txt",
            f"python3 main.py -p -n {parl_num}",
        ]
        batch = ";".join(commands)
        p = subprocess.Popen(f'plink -i {self.PRIVATE_KEY} -batch sgparl@{host} "{batch}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p.wait()