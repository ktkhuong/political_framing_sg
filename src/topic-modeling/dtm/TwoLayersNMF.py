import numpy as np
from models.TimeWindow import TimeWindow
from models.Topic import Topic
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
import pickle
import warnings
import logging

class DynamicTopics:
    def __init__(self, topics, coherence) -> None:
        self.topics = topics
        self.coherence = coherence

    @property
    def wt2dt(self):
        """
        Assuming a single membership model, i.e. each speech belongs to 1 dynamic topic with the highest weight 
        """
        W = np.array([topic.document_weights for topic in self.topics]).T
        return np.argmax(W, axis=1)

class TwoLayersNMF(BaseEstimator, TransformerMixin):
    N_COHERENCE_WORDS = 10
    N_DYNAMIC_TOP_TERMS = 20

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        w2v, vocab, time_windows = X
        time_windows = self.fit_window_topics(time_windows, vocab, w2v)
        dynamic_topics = self.fit_dynamic_topics(time_windows, vocab, w2v)
        return time_windows, dynamic_topics

    def fit_window_topics(self, time_windows, vocab, w2v):
        logger = logging.getLogger(__name__)

        for time_window in time_windows:
            topics, coherence = choose_topics(
                time_window.tfidf_matrix, 
                vocab, 
                w2v, 
                #min_n_components=time_window.n_titles-20, 
                #max_n_components=time_window.n_titles+20,
            )
            for i, topic in enumerate(topics):
                topic.id = f"{time_window.id}/{i}"
            time_window.topics = topics
            time_window.coherence = coherence
            logger.info(f"{time_window.id}: {time_window.n_titles} titles; {time_window.num_speeches} speeches; {time_window.num_topics} topics; {time_window.coherence} coherence;")
        return time_windows

    def fit_dynamic_topics(self, time_windows, vocab, w2v,min_n_components=30, max_n_components=50):
        logger = logging.getLogger(__name__)

        stacked = np.vstack([time_window.top_term_weights(self.N_DYNAMIC_TOP_TERMS) for time_window in time_windows])
        keep_terms = stacked.sum(axis=0) != 0
        keep_term_names = np.array(vocab)[keep_terms]
        reduced = stacked[:,keep_terms]
        tfidf_matrix = normalize(reduced, axis=1, norm='l2')
        topics, coherence = choose_topics(
            tfidf_matrix, 
            keep_term_names, 
            w2v, 
            min_n_components, 
            min(max_n_components, tfidf_matrix.shape[0])
        )
        logger.info(f"Dynamic topics: {len(topics)} topics; coherence = {coherence}")
        return DynamicTopics(topics, coherence)

def choose_topics(tfidf_matrix, vocab, w2v, min_n_components=10, max_n_components=25):
    best_coherence = float('-inf')
    best_topics = None
    coherences = []
    for n_components in range(min_n_components, max_n_components+1):
        w, h = fit_nmf(tfidf_matrix, n_components)
        topics = [Topic(term_weights, doc_weights, vocab) for term_weights, doc_weights in zip(h, w.T)]

        avg_coherence = sum(topic.coherence(w2v) for topic in topics) / len(topics)
        coherences.append(avg_coherence)
        if avg_coherence > best_coherence:
            best_coherence = avg_coherence
            best_topics = topics

    return best_topics, best_coherence

def fit_nmf(tfidf_matrix, n_components):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = NMF(n_components=n_components, init='nndsvd', solver='mu')
        w = model.fit_transform(tfidf_matrix)
        h = model.components_
    return w, h