import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from preprocess import preprocess_df

class PreprocessSpeeches(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        #df = preprocess_df(df, df_members['name'].values)
        return df