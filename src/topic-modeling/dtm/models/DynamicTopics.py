import numpy as np

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
        W = np.array([topic.document_weights for topic in self.topics]).T
        return np.argmax(W, axis=1)