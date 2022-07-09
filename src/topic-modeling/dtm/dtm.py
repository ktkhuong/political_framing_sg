import os
import getopt, sys
import pandas as pd
from utils import from_date, to_date
from tokenizer import Tokenizer
from models import TwoLayersNMF
import logging

logging.basicConfig()

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
    
    df = pd.read_csv(csv_fp, usecols=["date", "quarter", "section", "title", "member", "preprocessed_speech"])
    df['date'] = pd.to_datetime(df['date'])
    if start_date and end_date:
        df = from_date(df, "date", start_date)
        df = to_date(df, "date", end_date)
    df = df.sort_values("date").reset_index(drop=True)

    tokenized = Tokenizer().tokenize(df["preprocessed_speech"].values)

    model = TwoLayersNMF.by_w2v(tokenized)
    #model.fit()
    #tfidf = train_tfidf(tokenized)

if __name__ == "__main__":
    main()