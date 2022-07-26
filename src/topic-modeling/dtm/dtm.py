import os, getopt, sys, logging
from sklearn.pipeline import Pipeline
from pipelines.steps.FilterByDates import FilterByDates
from pipelines.steps.FitCvAndTfidf import FitCvAndTfidf
from pipelines.steps.FitDynamicTopics import FitDynamicTopics
from pipelines.steps.FitWindowTopics import FitWindowTopics
from pipelines.steps.PreprocessDataset import PreprocessDataset
from pipelines.steps.SaveDataFrameToDb import SaveDataFrameToDb
from pipelines.steps.SaveToDb import SaveToDb
from pipelines.steps.SetupVirtualMachines import SetupVirtualMachines
from pipelines.steps.SortByDates import SortByDates
from pipelines.steps.ReadDataset import ReadDataset
from pipelines.steps.RemoveShortSpeeches import RemoveShortSpeeches
from pipelines.steps.TokenizeSpeeches import TokenizeSpeeches
from pipelines.steps.FitWord2VecAndTfidf import FitWord2VecAndTfidf
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
    level=MESSAGE
)

VIRTUAL_MACHINES = [
    ("34.105.198.81", "europe-west2-c"),
    ("34.142.117.55", "europe-west2-c"),
    ("34.105.150.137", "europe-west2-c"),
    ("35.197.243.136", "europe-west2-c"),
    ("34.105.223.204", "europe-west2-c"),
    ("34.105.150.137", "europe-west2-c"),
    ("35.242.189.94", "europe-west2-c"),
    ("35.197.243.136", "europe-west2-c"),
    ("34.159.79.175", "europe-west3-c"),
    ("34.89.197.49", "europe-west3-c"),
    ("34.141.53.127", "europe-west3-c"),
    ("34.141.5.49", "europe-west3-c"),
    ("34.159.18.247", "europe-west3-c"),
    ("35.242.244.194", "europe-west3-c"),
    ("34.159.212.162", "europe-west3-c"),
    ("34.89.198.67", "europe-west3-c"),
    ("35.233.114.39", "europe-west1-b"),
    ("34.79.46.120", "europe-west1-b"),
    ("34.76.181.226", "europe-west1-b"),
    ("35.205.126.153", "europe-west1-b"),
    ("34.79.16.118", "europe-west1-b"),
    ("35.190.204.12", "europe-west1-b"),
    ("34.77.120.239", "europe-west1-b"),
    ("35.241.181.102", "europe-west1-b"),
]

COHERENCE_W2V = "w2v"
COHERENCE_CV = "cv"

def main():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-u", "--url", action="store", type="string", dest="url", help="url to dataset", default=None)
    parser.add_option("-f", "--from", action="store", type="string", dest="start_date", help="starting date", default=None)
    parser.add_option("-t", "--to", action="store", type="string", dest="end_date", help="end date", default=None)
    parser.add_option("-m", "--machines", action="store", type=int, dest="machines", help="number of available virtual machines", default=len(VIRTUAL_MACHINES))
    parser.add_option("-x", "--max-df", action="store", type=float, dest="max_df", help="max_df of TF-IDF", default=0.2)
    parser.add_option("-k", "--krange", action="store", type="string", dest="krange", help="range of num of window topics, comma separated", default="5,30")
    parser.add_option("-s", "--max-features", action="store", type=int, dest="max_features", help="max features of TF-IDF", default=None)
    (options, args) = parser.parse_args()
    if options.url == None:
        parser.error("Must specify URL to dataset")

    for path in ["out", "in"]:
        if not os.path.exists(path):
            os.makedirs(path)

    min_k, max_k = list(map(int, options.krange.split(",")))

    pipeline = Pipeline(
        steps=[
            ("Setup virtual machines", SetupVirtualMachines(VIRTUAL_MACHINES[:options.machines])),
            #("Preprocess dataset", PreprocessDataset(VIRTUAL_MACHINES[:machines], url)),
            ("Read dataset", ReadDataset()),
            ("Filter data frame by dates", FilterByDates(options.start_date, options.end_date)),
            ("Remove short speeches", RemoveShortSpeeches()),
            ("Sort data frame by dates", SortByDates()),
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Save data frame to db", SaveDataFrameToDb()),
            ("Two-layers NMF", Pipeline(
                steps=[
                    ("Fit Word2Vec And TF-IDF", FitWord2VecAndTfidf(max_df=options.max_df, max_features=options.max_features)),
                    ("Partition to time windows", PartitionToTimeWindows()),
                    ("Export pickles", ExportData()),
                    ("Fit window topics", FitWindowTopics(VIRTUAL_MACHINES[:options.machines], min_n_components=min_k, max_n_components=max_k)),
                    ("Fit dynamic topics", FitDynamicTopics(min_n_components=10, max_n_components=120, n_terms=20)),
                ]
            )),
            ("Save to db", SaveToDb()),
        ],
        verbose = True
    )
    pipeline.fit_transform(None)
    
if __name__ == "__main__":
    main()
