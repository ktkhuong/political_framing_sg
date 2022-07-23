from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
import logging
from models.Topic import Topic
from models.DynamicTopics import DynamicTopics
import warnings

class FitDynamicTopics(BaseEstimator, TransformerMixin):
    def __init__(self, min_n_components=25, max_n_components=90, n_terms=20):
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.n_terms = n_terms

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        coherence_model, vocab, time_windows = X
        stacked = np.vstack([time_window.top_term_weights(self.n_terms) for time_window in time_windows])
        keep_terms = stacked.sum(axis=0) != 0
        keep_term_names = np.array(vocab)[keep_terms]
        reduced = stacked[:,keep_terms]
        tfidf_matrix = normalize(reduced, axis=1, norm='l2')
        topics, coherence = self.choose_topics(
            tfidf_matrix, 
            keep_term_names, 
            coherence_model, 
            self.min_n_components, 
            min(self.max_n_components, tfidf_matrix.shape[0])
        )
        logger.message(f"Dynamic topics: {len(topics)} topics; coherence = {coherence}")
        return DynamicTopics(topics, coherence, time_windows)

    def choose_topics(self, tfidf_matrix, vocab, coherence_model, min_n_components=10, max_n_components=25):
        logger = logging.getLogger(__name__)

        best_coherence = float('-inf')
        best_topics = None
        coherences = []
        for n_components in range(min_n_components, max_n_components+1):
            w, h = self.fit_nmf(tfidf_matrix, n_components)
            topics = [Topic(term_weights, doc_weights, vocab) for term_weights, doc_weights in zip(h, w.T)]

            avg_coherence = sum(coherence_model.compute_coherence(topic) for topic in topics) / len(topics)
            coherences.append(avg_coherence)
            if avg_coherence > best_coherence:
                best_coherence = avg_coherence
                best_topics = topics
            logger.message(f"k = {n_components}; coherence = {avg_coherence}")
        logger.message(f"Best: k = {len(best_topics)}; coherence = {best_coherence}")
        return best_topics, best_coherence

    def fit_nmf(self, tfidf_matrix, n_components):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = NMF(n_components=n_components, init='nndsvd', solver='mu')
            w = model.fit_transform(tfidf_matrix)
            h = model.components_
        return w, h