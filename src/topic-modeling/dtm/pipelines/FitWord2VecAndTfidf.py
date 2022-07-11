import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

class FitWord2VecAndTfidf(BaseEstimator, TransformerMixin):
    def __init__(self, min_count=1, max_df=0.2, min_df=5):
        self.min_count = min_count
        self.max_df = max_df
        self.min_df = min_df

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        speeches = df["tokenized_speech"].values
        w2v = Word2Vec([speech.split() for speech in speeches], min_count=self.min_count)
        tfidf = TfidfVectorizer(norm='l2', max_df=self.max_df, min_df=self.min_df)
        tfidf.fit(speeches)
        return df, w2v, tfidf