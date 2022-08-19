from copyreg import pickle
from models.TimeWindow import TimeWindow
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

class PartitionToTimeWindows(BaseEstimator, TransformerMixin):
    def __init__(self, min_df=5, max_df=0.9, max_features=None):
        self.max_df = max_df
        self.min_df = min_df
        self.max_features = max_features

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df, coherence_model = X
        time_windows = self.partition_by_quarter(df)
        return coherence_model, time_windows

    def partition_by_quarter(self, df):
        logger = logging.getLogger(__name__)

        time_windows = []
        year_start = df["date"].dt.year.min()
        year_end = df["date"].dt.year.max()
        logger.message(f"Dataset shape: {df.shape}")
        for year in range(year_start, year_end+1):
            for quarter in range(1,5):
                df_quater = df[(df["date"].dt.year == year) & (df["date"].dt.quarter == quarter)]
                records = df_quater.index.values

                if len(records) > 0: 
                    quarterly_speeches = df["tokenized_speech"].values[records]
                    tfidf = TfidfVectorizer(norm='l2', max_df=self.max_df, min_df=self.min_df, max_features=self.max_features)
                    tfidf_matrix = tfidf.fit_transform(quarterly_speeches)
                    window = TimeWindow(
                        f"{year}Q{quarter}", 
                        records,
                        tfidf_matrix,
                        tfidf.get_feature_names_out()
                    )
                    time_windows.append(window)
                    logger.message(f"{window.id}: {df_quater.shape}")
                    logger.message(f"{window.id} TF-IDF: {tfidf_matrix.shape}")
                else:
                    logger.warning(f"{year}Q{quarter} is empty!")

        return time_windows