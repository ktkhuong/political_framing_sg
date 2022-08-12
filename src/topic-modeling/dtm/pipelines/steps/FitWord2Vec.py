import pandas as pd
from models.CoherenceModel import Word2VecCoherenceModel
from sklearn.base import BaseEstimator, TransformerMixin
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings

class FitWord2Vec(BaseEstimator, TransformerMixin):
    def __init__(self, min_count=5):
        self.min_count = min_count

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):        
        df = X
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            speeches = df["tokenized_speech"].values
            w2v = Word2Vec([speech.split() for speech in speeches], min_count=self.min_count, vector_size=500, sg=0, window=5)
            coherence_model = Word2VecCoherenceModel(w2v)
        return df, coherence_model