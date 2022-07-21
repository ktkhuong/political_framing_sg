from sklearn.base import BaseEstimator, TransformerMixin
import pickle
from models.CoherenceModel import Word2VecCoherenceModel, CvCoherenceModel
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
        if type(coherence_model) is Word2VecCoherenceModel:
            coherence_model.save(f"{self.EXPORT_PATH}/w2v.model")
        elif type(coherence_model) is CvCoherenceModel:
            coherence_model.save(f"{self.EXPORT_PATH}/cv.model")
        else:
            raise RuntimeError("Unknown coherence model!")
        with open(f'{self.EXPORT_PATH}/vocab.pkl', 'wb') as f:
            pickle.dump(vocab, f)
        return X

