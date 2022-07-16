import os
import getopt, sys
import pandas as pd
from TwoLayersNMF import TwoLayersNMF
import logging
from sklearn.pipeline import Pipeline, FeatureUnion
from pipelines.steps.FilterByDates import FilterByDates
from pipelines.steps.SaveDataFrameToDb import SaveDataFrameToDb
from pipelines.steps.SaveDynamicTopicsToDb import SaveDynamicTopicsToDb
from pipelines.steps.SaveWindowTopicsToDb import SaveWindowTopicsToDb
from pipelines.steps.SortByDates import SortByDates
from pipelines.steps.ReadDataset import ReadDataset
from pipelines.steps.RemoveShortSpeeches import RemoveShortSpeeches
from pipelines.steps.TokenizeSpeeches import TokenizeSpeeches
from pipelines.steps.FitWord2VecAndTfidf import FitWord2VecAndTfidf
from pipelines.steps.BuildTimeWindows import BuildTimeWindows
from pipelines.steps.ExportPickles import ExportPickles
#from pipelines.PartitionDataFrameIntoTimeWindows import PartitionDataFrameIntoTimeWindows

logging.basicConfig(
    format="[%(levelname)s] - %(asctime)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", 
    level=logging.INFO
)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:s:e:v")
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    csv_fp, start_date, end_date = "", "", ""
    verbose = False
    for o, a in opts:
        if o == "-f":
            csv_fp = a
        elif o == "-s":
            start_date = a
        elif o == "-e":
            end_date = a
        elif o == "-v":
            verbose = True
        else:
            pass

    if not os.path.exists("out"):
        os.makedirs("out")

    pipeline = Pipeline(
        steps=[
            ("Read dataset", ReadDataset(csv_fp)),
            ("Filter data frame by dates", FilterByDates(start_date, end_date)),
            # TODO: preprocess here
            ("Remove short speeches", RemoveShortSpeeches()),
            ("Sort data frame by dates", SortByDates()),
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Save data frame to db", SaveDataFrameToDb()),
            ("Fit Word2Vec And TF-IDF", FitWord2VecAndTfidf()),
            ("Build time windows", BuildTimeWindows()),
            ("Export to pickle", ExportPickles()),
            ("Model", TwoLayersNMF()),
            ("Save window topics to db", SaveWindowTopicsToDb()),
            ("Save dynamic topics to db", SaveDynamicTopicsToDb()),
        ],
        verbose = True
    )
    
    pipeline.fit_transform(None)

if __name__ == "__main__":
    main()
    #import numpy as np
    #a = np.arange(10,21)
    #print(np.where(a < 15))