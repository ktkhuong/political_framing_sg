import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class ReadDataset(BaseEstimator, TransformerMixin):
    def __init__(self, path):
        self.path = path

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        #logger = logging.getLogger(__name__)
        #logger.info(f"Read dataset")

        df = pd.read_csv(self.path, usecols=["date", "quarter", "section", "title", "member", "preprocessed_speech"])
        df['date'] = pd.to_datetime(df['date'])
        return df
