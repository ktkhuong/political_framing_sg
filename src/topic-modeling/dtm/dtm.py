import os, getopt, sys, logging
from sklearn.pipeline import Pipeline
from pipelines.steps.FilterByDates import FilterByDates
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
from pipelines.steps.BuildTimeWindows import BuildTimeWindows
from pipelines.steps.ExportData import ExportData

MESSAGE = logging.INFO+5
logging.addLevelName(MESSAGE, 'MESSAGE')  # addLevelName(25, 'MESSAGE')
def message(self, msg, *args, **kwargs):
    if self.isEnabledFor(MESSAGE):
        self._log(MESSAGE, msg, args, **kwargs) 
logging.message = message
logging.Logger.message = message
logging.basicConfig(
    format="[%(levelname)s] - %(asctime)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", 
    level=MESSAGE
)

VIRTUAL_MACHINES = [
    ("35.230.145.133", "europe-west2-c"),
    ("34.105.198.81", "europe-west2-c"),
    ("34.89.82.234", "europe-west2-c"),
    ("34.105.223.204", "europe-west2-c"),
    ("34.142.117.55", "europe-west2-c"),
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

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:s:e:m:")
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    url, start_date, end_date = "", "", ""
    machines = len(VIRTUAL_MACHINES)
    for o, a in opts:
        if o == "-u":
            url = a
        elif o == "-s":
            start_date = a
        elif o == "-e":
            end_date = a
        elif o == "-m":
            machines = int(a)
        else:
            pass

    for path in ["out", "in"]:
        if not os.path.exists(path):
            os.makedirs(path)

    pipeline = Pipeline(
        steps=[
            ("Setup virtual machines", SetupVirtualMachines(VIRTUAL_MACHINES[:machines])),
            ("Preprocess dataset", PreprocessDataset(VIRTUAL_MACHINES[:machines], url)),
            ("Read dataset", ReadDataset()),
            ("Filter data frame by dates", FilterByDates(start_date, end_date)),
            ("Remove short speeches", RemoveShortSpeeches()),
            ("Sort data frame by dates", SortByDates()),
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Save data frame to db", SaveDataFrameToDb()),
            ("Two-layers NMF", Pipeline(
                steps=[
                    ("Fit Word2Vec And TF-IDF", FitWord2VecAndTfidf()),
                    ("Build time windows", BuildTimeWindows()),
                    ("Export pickles", ExportData()),
                    ("Fit window topics", FitWindowTopics(VIRTUAL_MACHINES[:machines])),
                    ("Fit dynamic topics", FitDynamicTopics()),
                ]
            )),
            ("Save to db", SaveToDb()),
        ],
        verbose = True
    )
    pipeline.fit_transform(None)
    
if __name__ == "__main__":
    main()
