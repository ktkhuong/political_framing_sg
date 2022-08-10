import numpy as np
import pickle

class DynamicTopics:
    def __init__(self, topics, coherence, time_windows) -> None:
        self.time_windows = time_windows
        self.topics = topics
        self.coherence = coherence

    @property
    def wt2dt(self):
        """
        Assuming a single membership model, i.e. each window topic belongs to 1 dynamic topic with the highest weight 
        """
        return np.argmax(self.W, axis=1)

    @property
    def W(self):
        return np.array([topic.document_weights for topic in self.topics]).T

    @property
    def H(self):
        return np.array([topic.term_weights for topic in self.topics])

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)