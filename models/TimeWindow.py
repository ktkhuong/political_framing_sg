import numpy as np
import pickle, logging
import pandas as pd
from nmf import choose_topics
from sklearn.preprocessing import normalize

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

        self.fit_children(coherence_model, 5, 15)
 
        if self.id.find("/") == -1: # only applicable to root
            logger.info(f"Assign extra topics to leaf topic...")
            topics = self.topics[:]
            for child in self.children:
                topics += child.topics[:]

        if self.id.find("/") == -1: # only applicable to root
            self.save(f"{self.OUT_PATH}/{self.id}.pkl")
        
        logger.info(f"{self.id}: {self.num_speeches} speeches; {self.num_topics} topics; coherence = {self.coherence};")
        logger.info("-----------------------------------------------------------------------------")

    def fit_children(self, coherence_model, min_k, max_k):
        logger = logging.getLogger(__name__)
        logger.info(f">>> Fitting {self.id} children ...")

        popular_topics = self.popular_topics
        x = np.argmax(self.W, axis=1)
        for pt in popular_topics:
            rows = np.where(x == pt)
            tfidf_matrix = normalize(self.tfidf_matrix[rows], axis=1, norm='l2')
            child = TimeWindow(
                f"{self.id}/{pt}",
                self.speech_ids[rows],
                tfidf_matrix,
                self.vocab
            )
            child.fit(coherence_model, min_k, max_k)
            self.children.append(child)

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
    def extra_speeches(self):
        max_weights = np.max(self.W, axis=1)
        return np.where(max_weights < 0.05)

    @property
    def assigned_speeches(self):
        max_weights = np.max(self.W, axis=1)
        return np.where(max_weights >= 0.05)

    @property
    def popular_topics(self):
        rows = self.assigned_speeches
        W = self.W[rows]
        _, n_topics = W.shape
        x = np.argmax(W, axis=1)
        hist, _ = np.histogram(x, bins=range(n_topics+1))
        return np.array([i for i, freq in enumerate(hist) if freq > 25])
    
    @property
    def leaf_topics(self):
        rows = self.assigned_speeches
        W = self.W[rows]
        _, n_topics = W.shape
        x = np.argmax(W, axis=1)
        hist, _ = np.histogram(x, bins=range(n_topics+1))
        return np.array([i for i, freq in enumerate(hist) if freq < 25])

    @property
    def speech2topic(self):
        """
        Assuming a single membership model, i.e. each speech has 1 topic with the highest weight 
        """
        #return {self.speech_ids[i]: (self.topics[topic].id, self.W[i,topic]) for i, topic in enumerate(np.argmax(self.W, axis=1))}
        #topics = np.array([np.argmax(self.W[i]) for i in self.assigned_speeches])
        topics = np.argmax(self.W[self.assigned_speeches], axis=1)
        return {self.speech_ids[speech]: (self.topics[topic], self.W[speech, topic]) for speech, topic in zip(self.assigned_speeches, topics)}

    def top_term_weights(self, n_top):
        return [topic.top_term_weights(n_top) for topic in self.topics]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)