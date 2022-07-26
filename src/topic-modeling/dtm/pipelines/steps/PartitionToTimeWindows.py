from copyreg import pickle
from models.TimeWindow import TimeWindow
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class PartitionToTimeWindows(BaseEstimator, TransformerMixin):
    WINDOW_SIZE_MONTH = 'month'
    WINDOW_SIZE_QUARTER = 'quarter'

    def __init__(self, window_size=WINDOW_SIZE_QUARTER):
        self.window_size = window_size

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        df, coherence_model, tfidf = X
        tfidf_matrix = tfidf.transform(df["tokenized_speech"].values)

        logger.message(f"DataFrame: {df.shape}")
        logger.message(f"TF-IDF: {tfidf_matrix.shape}")
        
        if self.window_size == self.WINDOW_SIZE_MONTH:
            time_windows = self.partition_by_month(df, tfidf_matrix)
        elif self.window_size == self.WINDOW_SIZE_QUARTER:
            time_windows = self.partition_by_quarter(df, tfidf_matrix)
        else:
            raise RuntimeError("Unsupported window size!")
        vocab = tfidf.get_feature_names_out()
        return coherence_model, vocab, time_windows

    def partition_by_month(self, df, tfidf_matrix):
        logger = logging.getLogger(__name__)

        time_windows = []
        year_start = df["date"].dt.year.min()
        year_end = df["date"].dt.year.max()
        for year in range(year_start, year_end+1):
            for month in range(1,13):
                df_month = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]
                records = df_month.index.values
                if len(records) > 0: 
                    window = TimeWindow(
                        f"{year}M{month}", 
                        records,
                        tfidf_matrix[records], 
                        df_month["title"].nunique()
                    )
                    time_windows.append(window)
                    logger.message(f"{year}M{month}: {df_month.shape}")
                else:
                    logger.warning(f"{year}M{month} is empty!")

        return time_windows

    def partition_by_quarter(self, df, tfidf_matrix):
        logger = logging.getLogger(__name__)

        time_windows = []
        year_start = df["date"].dt.year.min()
        year_end = df["date"].dt.year.max()
        for year in range(year_start, year_end+1):
            for quarter in range(1,5):
                df_quater = df[(df["date"].dt.year == year) & (df["date"].dt.quarter == quarter)]
                records = df_quater.index.values
                if len(records) > 0: 
                    window = TimeWindow(
                        f"{year}Q{quarter}", 
                        records,
                        tfidf_matrix[records], 
                        df_quater["title"].nunique()
                    )
                    time_windows.append(window)
                    logger.message(f"{year}Q{quarter}: {df_quater.shape}")
                else:
                    logger.warning(f"{year}Q{quarter} is empty!")

        return time_windows