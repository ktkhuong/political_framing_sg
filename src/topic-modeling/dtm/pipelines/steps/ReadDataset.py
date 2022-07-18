import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging
import os

class ReadDataset(BaseEstimator, TransformerMixin):
    DATASET_PATH = "in"

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        frames = [pd.read_csv(f"{self.DATASET_PATH}/{f}", usecols=["date", "quarter", "section", "title", "member", "preprocessed_speech"])
                    for f in os.listdir(self.DATASET_PATH) if f.endswith(".csv")]
        for frame in frames:
            frame['date'] = pd.to_datetime(frame['date'])
        df = pd.concat(frames)
        
        logger.message(f"Dataset shape: {df.shape}")
        return df