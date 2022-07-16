from sklearn.base import BaseEstimator, TransformerMixin
import pickle

class ExportPickles(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        w2v, vocab, time_windows = X
        for window in time_windows:
            window.save(f"out/{window.id}.pkl")
        w2v.save("out/w2v.model")
        with open('out/vocab.pkl', 'wb') as f:
            pickle.dump(vocab, f)
        return X

