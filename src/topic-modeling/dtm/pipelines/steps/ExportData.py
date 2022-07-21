from sklearn.base import BaseEstimator, TransformerMixin
import pickle

class ExportData(BaseEstimator, TransformerMixin):
    EXPORT_PATH = 'out'

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        coherence_model, vocab, time_windows = X
        for window in time_windows:
            window.save(f"{self.EXPORT_PATH}/{window.id}.pkl")
        coherence_model.save("{self.EXPORT_PATH}/coherence_model.model")
        with open('{self.EXPORT_PATH}/vocab.pkl', 'wb') as f:
            pickle.dump(vocab, f)
        return X

