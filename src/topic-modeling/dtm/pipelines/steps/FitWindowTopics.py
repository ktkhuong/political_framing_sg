from time import sleep
from regex import I
from sklearn.base import BaseEstimator, TransformerMixin
import os, subprocess, logging
import threading
from models.TimeWindow import TimeWindow

class FitWindowTopics(BaseEstimator, TransformerMixin):
    PRIVATE_KEY = "ssh/sgparl_private.ppk"

    def __init__(self, machines, min_n_components=10, max_n_components=25):
        self.machines = machines
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        coherence_model, time_windows = X

        used = self.upload_data()
        self.run_machine(used, self.fit_windows)
        self.download_data(used)
        time_windows = self.concat()

        return coherence_model, time_windows

    def run_machine(self, used, target):
        threads = []
        for i in used:
            host, _ = self.machines[i-1]
            t = threading.Thread(target=target, args=(host,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
    def fit_windows(self, host):
        commands = [
            "sudo wget -P cloud/data -c https://github.com/ktkhuong/sgparl/releases/download/w2v_npap/w2v.model",
            #"sudo wget -P cloud/data -c https://github.com/ktkhuong/sgparl/releases/download/w2v_npap/w2v.model.syn1neg.npy",
            #"sudo wget -P cloud/data -c https://github.com/ktkhuong/sgparl/releases/download/w2v_npap/w2v.model.wv.vectors.npy",
            "cd cloud",
            "python3 -m venv env",
            "source env/bin/activate",
            "pip install -r requirements.txt",
            f"python3 main.py -f -k {self.min_n_components},{self.max_n_components}",
        ]
        batch = ";".join(commands)
        p = subprocess.Popen(f'plink -i {self.PRIVATE_KEY} -batch sgparl@{host} "{batch}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p.wait()

    def upload_data(self):
        logger = logging.getLogger(__name__)

        years = list(set([f[:4] for f in os.listdir("out") if f.endswith(".pkl") and not f.startswith("vocab")]))
        years.sort()
        used = set()
        i = 1
        for year in years:
            logger.message(f"Upload to machine{str(i).zfill(2)}: {year}")
            _, zone = self.machines[i-1]
            used.add(i)
            p = subprocess.Popen(f"gcloud compute scp --recurse --zone={zone} out/{year}*.pkl machine{str(i).zfill(2)}:/home/sgparl/cloud/data", shell=True)
            p.wait()
            #p = subprocess.Popen(f"gcloud compute scp --recurse --zone={zone} out/w2v.model machine{str(i).zfill(2)}:/home/sgparl/cloud/data", shell=True)
            #p.wait()
            i += 1
            # load balancing: round-robin
            if i > len(self.machines):
                i = 1
        return used

    def download_data(self, used):
        logger = logging.getLogger(__name__)

        for i in used:
            logger.message(f"Download from machine{str(i).zfill(2)}")
            _, zone = self.machines[i-1]
            p = subprocess.Popen(f"gcloud compute scp --recurse --zone={zone} machine{str(i).zfill(2)}:/home/sgparl/cloud/out/* in", shell=True)
            p.wait()

    def concat(self):
        logger = logging.getLogger(__name__)

        paths = ["in/"+f for f in os.listdir("in") if f.endswith(".pkl")]
        paths.sort()
        time_windows = [TimeWindow.load(path) for path in paths]
        for time_window in time_windows:
            logger.message(f"Loading window {time_window.id} ...")
        return time_windows
