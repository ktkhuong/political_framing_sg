import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging
import os

class ReadDataset(BaseEstimator, TransformerMixin):
    DATASET_PATH = "in"

    def __init__(self, party):
        self.party = party

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        frames = [pd.read_csv(f"{self.DATASET_PATH}/{f}", usecols=["date", "quarter", "section", "title", "member", "preprocessed_speech", "party"])
                    for f in os.listdir(self.DATASET_PATH) if f.endswith(".csv")]
        df = pd.concat(frames)
        df['date'] = pd.to_datetime(df['date'])
        if self.party != 'all':
            df = df[df["party"] == self.party]
        logger.message(f"Dataset shape: {df.shape}")
        return df