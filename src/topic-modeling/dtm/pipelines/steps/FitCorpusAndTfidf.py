import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from gensim.corpora.dictionary import Dictionary
from sklearn.feature_extraction.text import TfidfVectorizer
from models.CoherenceModel import CvCoherenceModel
import warnings

class FitWord2VecAndTfidf(BaseEstimator, TransformerMixin):
    def __init__(self, min_count=1, max_df=0.2, min_df=5):
        self.min_count = min_count
        self.max_df = max_df
        self.min_df = min_df

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):        
        df = X
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            texts = [speech.split() for speech in df["tokenized_speech"].values]
            dictionary = Dictionary(texts)
            corpus = texts#[dictionary.doc2bow(text) for text in texts]
            coherence_model = CvCoherenceModel(corpus=corpus, dictionary=dictionary)
            tfidf = TfidfVectorizer(norm='l2', max_df=self.max_df, min_df=self.min_df)
            tfidf.fit(df["tokenized_speech"].values)
        return df, coherence_model, tfidf