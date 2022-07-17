from copyreg import pickle
from models.TimeWindow import TimeWindow
from sklearn.base import BaseEstimator, TransformerMixin
import logging

class BuildTimeWindows(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        df, w2v, tfidf = X
        tfidf_matrix = tfidf.transform(df["tokenized_speech"].values)

        logger.message(f"DataFrame: {df.shape}")
        logger.message(f"TF-IDF: {tfidf_matrix.shape}")
        
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
        vocab = tfidf.get_feature_names_out()
        return w2v, vocab, time_windows
