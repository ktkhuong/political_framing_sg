import os
import getopt, sys
import pandas as pd
#from utils import from_date, to_date
from gensim.models import Word2Vec
from models import TwoLayersNMF
import logging
from sklearn.pipeline import Pipeline, FeatureUnion
from pipelines.FilterAndSortDataFrameByDates import FilterAndSortDataFrameByDates
from pipelines.ReadDataset import ReadDataset
from pipelines.TokenizeSpeeches import TokenizeSpeeches
from pipelines.FitWord2VecAndTfidf import FitWord2VecAndTfidf
from pipelines.BuildTimeWindows import BuildTimeWindows
#from pipelines.PartitionDataFrameIntoTimeWindows import PartitionDataFrameIntoTimeWindows

logging.basicConfig(
    format="[%(levelname)s] - %(asctime)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s", 
    #level=logging.INFO
)

"""
def read_csv(file_path, start_date, end_date) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    logger.info(f"Read {file_path} to pandas DataFrame")

    df = pd.read_csv(file_path, usecols=["date", "quarter", "section", "title", "member", "preprocessed_speech"])
    df['date'] = pd.to_datetime(df['date'])
    if start_date and end_date:
        df = from_date(df, "date", start_date)
        df = to_date(df, "date", end_date)
    df = df.sort_values("date").reset_index(drop=True)
    return df
"""

def build_model(tokenized):
    logger = logging.getLogger(__name__)
    logger.info(f"Build TwoLayersNMF model")

    model = TwoLayersNMF.by_w2v(tokenized)

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

    pipeline = Pipeline(
        steps=[
            ("Read dataset", ReadDataset(csv_fp)),
            ("Filter data frame by dates", FilterAndSortDataFrameByDates(start_date, end_date)),
            # TODO: preprocess here
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Fit Word2Vec And TF-IDF", FitWord2VecAndTfidf()),
            ("Build time windows", BuildTimeWindows()),
            ()
        ],
        verbose = True
    )
    df = pipeline.fit_transform(None)
     
    #print(pipe.get_params())

    #model = TwoLayersNMF.by_w2v(tokenized)
    #model.fit()
    #tfidf = train_tfidf(tokenized)
    #x = read_csv(csv_fp)
    #print(x)

if __name__ == "__main__":
    main()