import pandas as pd
from models.CoherenceModel import Word2VecCoherenceModel
from sklearn.base import BaseEstimator, TransformerMixin
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

class FitWord2VecAndTfidf(BaseEstimator, TransformerMixin):
    def __init__(self, min_count=10, max_df=0.2, min_df=10, max_features=None):
        self.min_count = min_count
        self.max_df = max_df
        self.min_df = min_df
        self.max_features = max_features

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):        
        df = X
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            speeches = df["tokenized_speech"].values
            w2v = Word2Vec([speech.split() for speech in speeches], min_count=self.min_count, vector_size=500, sg=0, window=5)
            coherence_model = Word2VecCoherenceModel(w2v)            
            tfidf = TfidfVectorizer(norm='l2', max_df=self.max_df, min_df=self.min_df, max_features=self.max_features)
            tfidf.fit(speeches)
        return df, coherence_model, tfidf