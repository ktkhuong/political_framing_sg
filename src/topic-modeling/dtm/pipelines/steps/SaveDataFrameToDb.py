import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import sqlite3

class SaveDataFrameToDb(BaseEstimator, TransformerMixin):
    def __init__(self, table_name="dataframe", db_name="sgparl.db"):
        self.db_name = db_name
        self.table_name = table_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        conn = sqlite3.connect(self.db_name)
        #df.to_sql(name=self.table_name, con=conn)
        df.to_csv("sgparl_tokenized.csv")
        conn.close()
        return df