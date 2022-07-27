import numpy as np
import pickle, logging
import pandas as pd
from nmf import choose_topics

class TimeWindow:
    OUT_PATH = "out"

    def __init__(self, id, speech_ids, tfidf_matrix, vocab):
        self.id = id
        self.speech_ids = speech_ids
        self.tfidf_matrix = tfidf_matrix # TF-IDF of the time window
        self.vocab = vocab
        self.topics = [] # list of Topic
        self.coherence = 0
        self.children = []

    def fit(self, coherence_model, min_k, max_k):
        logger = logging.getLogger(__name__)
        logger.info(f"Fitting {self.id} ...")

        topics, coherence = choose_topics(
            self.tfidf_matrix, 
            self.vocab, 
            coherence_model, 
            min_n_components=min(min_k, self.num_speeches), 
            max_n_components=min(max_k, self.num_speeches),
        )
        for i, topic in enumerate(topics):
            topic.id = f"{self.id}/{i}"
        self.topics = topics
        self.coherence = coherence
        self.save(f"{self.OUT_PATH}/{self.id}.pkl")
        
        logger.info(f"{self.id}: {self.n_titles} titles; {self.num_speeches} speeches; {self.num_topics} topics; coherence = {self.coherence};")
        logger.info("-----------------------------------------------------------------------------")

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
    def W(self):
        return np.array([topic.document_weights for topic in self.topics]).T

    @property
    def speech2topic(self):
        """
        Assuming a single membership model, i.e. each speech has 1 topic with the highest weight 
        """
        return {self.speech_ids[i]: (self.topics[topic].id, self.W[i,topic]) for i, topic in enumerate(np.argmax(self.W, axis=1))}

    def top_term_weights(self, n_top):
        return [topic.top_term_weights(n_top) for topic in self.topics]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)