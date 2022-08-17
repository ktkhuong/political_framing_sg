import os, getopt, sys, logging
from sklearn.pipeline import Pipeline
from pipelines.steps.FilterByDates import FilterByDates
from pipelines.steps.FitCvAndTfidf import FitCvAndTfidf
from pipelines.steps.SecondLayerNMF import SecondLayerNMF
from pipelines.steps.FirstLayerNMF import FirstLayerNMF
from pipelines.steps.PreprocessDataset import PreprocessDataset
from pipelines.steps.SaveDataFrameToDb import SaveDataFrameToDb
from pipelines.steps.SaveToDb import SaveToDb
from pipelines.steps.SetupVirtualMachines import SetupVirtualMachines
from pipelines.steps.SortByDates import SortByDates
from pipelines.steps.ReadDataset import ReadDataset
from pipelines.steps.RemoveShortSpeeches import RemoveShortSpeeches
from pipelines.steps.TokenizeSpeeches import TokenizeSpeeches
from pipelines.steps.FitWord2Vec import FitWord2Vec
from pipelines.steps.PartitionToTimeWindows import PartitionToTimeWindows
from pipelines.steps.ExportData import ExportData
from models.CoherenceModel import CvCoherenceModel
from optparse import OptionParser

MESSAGE = logging.INFO+5
logging.addLevelName(MESSAGE, 'MESSAGE')  # addLevelName(25, 'MESSAGE')
def message(self, msg, *args, **kwargs):
    if self.isEnabledFor(MESSAGE):
        self._log(MESSAGE, msg, args, **kwargs) 
logging.message = message
logging.Logger.message = message
logging.basicConfig(
    format="[%(levelname)s] - %(asctime)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", 
    level=MESSAGE,
    handlers=[
        logging.FileHandler(f"dtm.log"),
        logging.StreamHandler()
    ]
)

VIRTUAL_MACHINES = [
    ("34.105.198.81", "europe-west2-c"),
    ("34.142.117.55", "europe-west2-c"),
    ("34.105.150.137", "europe-west2-c"),
    ("35.197.243.136", "europe-west2-c"),
    ("34.105.223.204", "europe-west2-c"),
    
    ("35.189.122.246", "europe-west2-c"),
    ("34.105.163.112", "europe-west2-c"),
    ("34.105.242.139", "europe-west2-c"),
    ("35.198.160.248", "europe-west3-c"),
    ("34.159.134.229", "europe-west3-c"),

    ("34.159.128.17", "europe-west3-c"),
    ("34.89.241.8", "europe-west3-c"),
    ("35.242.246.209", "europe-west3-c"),
    ("34.159.85.56", "europe-west3-c"),
    ("34.141.17.127", "europe-west3-c"),

    ("35.198.187.22", "europe-west3-c"),
    ("35.240.80.244", "europe-west1-b"),
    ("104.155.115.236", "europe-west1-b"),
    ("34.140.51.174", "europe-west1-b"),
    ("34.78.19.79", "europe-west1-b"),

    ("35.195.10.236", "europe-west1-b"),
    ("34.77.220.115", "europe-west1-b"),
    ("35.187.1.101", "europe-west1-b"),
    ("146.148.25.109", "europe-west1-b"),
]

COHERENCE_W2V = "w2v"
COHERENCE_CV = "cv"

def main():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-u", "--url", action="store", type="string", dest="url", help="url to dataset", default=None)
    parser.add_option("-f", "--from", action="store", type="string", dest="start_date", help="starting date", default=None)
    parser.add_option("-t", "--to", action="store", type="string", dest="end_date", help="end date", default=None)
    parser.add_option("-m", "--machines", action="store", type=int, dest="machines", help="number of available virtual machines", default=len(VIRTUAL_MACHINES))
    parser.add_option("-c", "--min-count", action="store", type=int, dest="min_count", help="min_count of W2V", default=5)
    parser.add_option("-x", "--max-df", action="store", type="string", dest="max_df", help="max_df of TF-IDF", default="1.0")
    parser.add_option("-y", "--min-df", action="store", type="string", dest="min_df", help="min_df of TF-IDF", default="1")
    parser.add_option("-k", "--krange", action="store", type="string", dest="krange", help="range of num of window topics, comma separated", default="15,40")
    parser.add_option("-d", "--drange", action="store", type="string", dest="drange", help="range of dynamic topics, comma separated", default="25,120")
    parser.add_option("-s", "--max-features", action="store", type=int, dest="max_features", help="max features of TF-IDF", default=None)
    parser.add_option("-p", "--party", action="store", type="string", dest="party", help="political party to be considered", default="all")
    (options, args) = parser.parse_args()
    if options.url == None:
        parser.error("Must specify URL to dataset")

    for path in ["out", "in"]:
        if not os.path.exists(path):
            os.makedirs(path)

    min_k, max_k = list(map(int, options.krange.split(",")))
    min_d, max_d = list(map(int, options.drange.split(",")))
    min_df = int(options.min_df) if options.min_df.find(".") == -1 else float(options.min_df)
    max_df = int(options.max_df) if options.max_df.find(".") == -1 else float(options.max_df)

    pipeline = Pipeline(
        steps=[
            ("Setup virtual machines", SetupVirtualMachines(VIRTUAL_MACHINES[:options.machines])),
            #("Preprocess dataset", PreprocessDataset(VIRTUAL_MACHINES[:options.machines], url)),
            ("Read dataset", ReadDataset(party=options.party)),
            ("Filter data frame by dates", FilterByDates(options.start_date, options.end_date)),
            ("Remove short speeches", RemoveShortSpeeches()),
            ("Sort data frame by dates", SortByDates()),
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Save data frame to db", SaveDataFrameToDb()),
            ("Two-layers NMF", Pipeline(
                steps=[
                    ("Fit Word2Vec And TF-IDF", FitWord2Vec(min_count=options.min_count)),
                    ("Partition to time windows", PartitionToTimeWindows(min_df=min_df, max_df=max_df, max_features=options.max_features)),
                    ("Export pickles", ExportData()),
                    ("First layer NMF", FirstLayerNMF(VIRTUAL_MACHINES[:options.machines], min_n_components=min_k, max_n_components=max_k)),
                    ("Second layer NMF", SecondLayerNMF(min_n_components=min_d, max_n_components=max_d, n_terms=20)),
                ]
            )),
            ("Save to db", SaveToDb()),
        ],
        verbose = True
    )
    pipeline.fit_transform(None)
    
if __name__ == "__main__":
    main()
