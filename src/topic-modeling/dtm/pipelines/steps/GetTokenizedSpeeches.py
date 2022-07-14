import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class GetTokenizedSpeeches(BaseEstimator, TransformerMixin):
    def __init__(self, col_date):
        self.col_date = col_date

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        df = X
        time_windows = []
        year_start = df[self.col_date].dt.year.min()
        year_end = df[self.col_date].dt.year.max()
        for year in range(year_start, year_end+1):
            for quarter in range(1,5):
                df_quater = df[(df[self.col_date].dt.year == year) & (df[self.col_date].dt.quarter == quarter)]
                time_window = df_quater.index.values
                if len(time_window) > 0: 
                    time_windows.append(vectorized[time_window])
                else:
                    logger.warning(f"{year}Q{quarter} is empty!")
        return df