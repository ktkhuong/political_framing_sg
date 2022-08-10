from unicodedata import normalize
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from sklearn.decomposition import NMF
from sklearn.preprocessing import Normalizer
import logging
from models.Topic import Topic
from nmf import choose_topics
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

        coherence_model, time_windows = X

        all_weights = []
        all_terms = []
        for time_window in time_windows:
            weights, terms = time_window.topic_weights()
            all_weights += weights
            all_terms += terms
        all_terms = list(set(all_terms))

        M = np.zeros( (len(all_weights), len(all_terms)) )
        term_col_map = {term: i for i, term in enumerate(all_terms)}
        
        for row, topic_weights in enumerate(all_weights):
            for term in topic_weights.keys():
                M[row, term_col_map[term]] = topic_weights[term]
        normalizer = Normalizer(norm='l2', copy=True)
        tfidf_matrix = normalizer.fit_transform(M)
        """
        stacked = np.vstack([time_window.top_term_weights(self.n_terms) for time_window in time_windows])
        keep_terms = stacked.sum(axis=0) != 0
        keep_term_names = np.array(vocab)[keep_terms]
        reduced = stacked[:,keep_terms]
        tfidf_matrix = normalize(reduced, axis=1, norm='l2')
        """
        topics, coherence = choose_topics(
            tfidf_matrix, 
            all_terms, 
            coherence_model, 
            self.min_n_components, 
            min(self.max_n_components, tfidf_matrix.shape[0])
        )
        logger.message(f"Dynamic topics: {len(topics)} topics; coherence = {coherence}")
        return DynamicTopics(topics, coherence, time_windows)