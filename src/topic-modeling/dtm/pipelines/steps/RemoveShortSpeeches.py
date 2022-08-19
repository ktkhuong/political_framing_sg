import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class RemoveShortSpeeches(BaseEstimator, TransformerMixin):
    DEFAULT_MIN_SPEECH_LENGTH = 40

    def __init__(self, min_speech_length = DEFAULT_MIN_SPEECH_LENGTH):
        self.min_speech_length = min_speech_length

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        df["word_count"] = df["preprocessed_speech"].map(lambda x: len(x.split()))
        df = df[df["word_count"] >= self.min_speech_length]
        df = df.drop(columns=['word_count'])
        return df