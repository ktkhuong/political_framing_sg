import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class FilterAndSortDataFrameByDates(BaseEstimator, TransformerMixin):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def fit(self, X, y=None):
        return self

    def to_date(self, df, col_date, date_in_str):
        if not date_in_str:
            return df
        return df[df[col_date] <= pd.Timestamp(date_in_str)]

    def from_date(self, df, col_date, date_in_str):
        if not date_in_str:
            return df
        return df[df[col_date] >= pd.Timestamp(date_in_str)]

    def transform(self, X, y=None):
        df = X
        df = self.from_date(df, "date", self.start_date)
        df = self.to_date(df, "date", self.end_date)
        df = df.sort_values("date").reset_index(drop=True)
        return df