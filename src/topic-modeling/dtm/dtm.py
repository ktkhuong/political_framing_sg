import os
import getopt, sys
import pandas as pd
from models import TwoLayersNMF
import logging
from sklearn.pipeline import Pipeline, FeatureUnion
from pipelines.FilterByDates import FilterByDates
from pipelines.SortByDates import SortByDates
from pipelines.ReadDataset import ReadDataset
from pipelines.RemoveShortSpeeches import RemoveShortSpeeches
from pipelines.TokenizeSpeeches import TokenizeSpeeches
from pipelines.FitWord2VecAndTfidf import FitWord2VecAndTfidf
from pipelines.BuildTimeWindows import BuildTimeWindows
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

    pipeline = Pipeline(
        steps=[
            ("Read dataset", ReadDataset(csv_fp)),
            ("Filter data frame by dates", FilterByDates(start_date, end_date)),
            # TODO: preprocess here
            ("Remove short speeches", RemoveShortSpeeches()),
            ("Sort data frame by dates", SortByDates()),
            ("Tokenize speeches", TokenizeSpeeches()),
            ("Fit Word2Vec And TF-IDF", FitWord2VecAndTfidf()),
            ("Build time windows", BuildTimeWindows()),
            ("Model", TwoLayersNMF()),
        ],
        verbose = True
    )
    df, time_windows = pipeline.fit_transform(None)

    for time_window in time_windows:
        print(f"{time_window.id}: {time_window.num_speeches} speeches; {time_window.num_topics} topics; {time_window.coherence} coherence")
        speech2topic = time_window.speech2topic
        df_topics = pd.DataFrame(speech2topic.items(), columns=["speech","topic"]).set_index("speech")
        df = pd.merge(df, df_topics, how="inner", left_index=True, right_index=True)

    df.sort_values(by=["topic","title"]).to_csv("sgparl_window_topics.csv")
        
    #print(pipe.get_params())

    #model = TwoLayersNMF.by_w2v(tokenized)
    #model.fit()
    #tfidf = train_tfidf(tokenized)
    #x = read_csv(csv_fp)
    #print(x)

if __name__ == "__main__":
    main()