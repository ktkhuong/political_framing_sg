import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class SortByDates(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        df = df.sort_values("date").reset_index(drop=True)
        return df