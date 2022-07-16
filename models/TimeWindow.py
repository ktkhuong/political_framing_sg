import pickle
import numpy as np

class TimeWindow:
    def __init__(self, id, speech_ids, tfidf_matrix, n_titles):
        self.id = id
        self.speech_ids = speech_ids
        self.tfidf_matrix = tfidf_matrix # TF-IDF of the time window
        self.topics = [] # list of Topic
        self.coherence = 0
        self.n_titles = n_titles

    @property
    def num_speeches(self):
        return self.tfidf_matrix.shape[0]

    @property
    def num_words(self):
        return self.tfidf_matrix.shape[1]

    @property
    def num_topics(self):
        return len(self.topics)

    @property
    def speech2topic(self):
        """
        Assuming a single membership model, i.e. each speech has 1 topic with the highest weight 
        """
        speech_topic_weights = np.array([topic.document_weights for topic in self.topics]).T # shape = (num_speeches, num_topics)
        return {self.speech_ids[speech]: self.topics[topic].id for speech, topic in enumerate(np.argmax(speech_topic_weights, axis=1))}

    def top_term_weights(self, n_top):
        return [topic.top_term_weights(n_top) for topic in self.topics]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)