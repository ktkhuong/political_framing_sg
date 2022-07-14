import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from itertools import combinations
from scipy import spatial
from gensim.models import Word2Vec
import pickle
import warnings
import logging
from pipelines.SaveDynamicTopicsToDb import SaveDynamicTopicsToDb

from pipelines.SaveWindowTopicsToDb import SaveWindowTopicsToDb

class Topic:
    N_TOP_TERMS = 10

    def __init__(self, term_weights, document_weights, vocab):
        self.term_weights = term_weights
        self.document_weights = document_weights
        self.vocab = vocab
        self.id = None

    def top_term_indices(self, n_top=N_TOP_TERMS):
        return np.argsort(self.term_weights)[::-1][:n_top]

    def top_terms(self, n_top=N_TOP_TERMS):
        top_indices = self.top_term_indices(n_top)
        return [self.vocab[i] for i in top_indices]

    def top_term_weights(self, n_top=N_TOP_TERMS):
        word_to_index = {w: i for i, w in enumerate(self.vocab)}
        row = np.zeros((len(self.vocab),))
        top_word_index = [word_to_index[word] for word in self.top_terms(n_top)]
        row[top_word_index] = self.term_weights[top_word_index]
        return row

    def coherence(self, w2v: Word2Vec):
        comb = list(combinations(self.top_terms(), 2))
        total_distance = sum(w2v.wv.similarity(wi, wj) for wi, wj in comb)
        return float(total_distance) / len(comb)

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

class DynamicTopics:
    def __init__(self, time_windows, vocab, w2v, min_n_components=30, max_n_components=50) -> None:
        stacked = np.vstack([time_window.top_term_weights(TwoLayersNMF.N_DYNAMIC_TOP_TERMS) for time_window in time_windows])
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
        df, w2v, vocab, time_windows = X
        pipeline = Pipeline(
            steps=[
                ("Fit window topics", FitWindowTopics()),
                ("Fit dynamic topics", FitDynamicTopics()),
            ],
            verbose=True
        )
        time_windows, dynamic_topics = pipeline.fit_transform((time_windows, vocab, w2v))
        return df, time_windows, dynamic_topics

class FitWindowTopics(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        logger = logging.getLogger(__name__)

        time_windows, vocab, w2v = X
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
        return time_windows, vocab, w2v

class FitDynamicTopics(BaseEstimator, TransformerMixin):
    def __init__(self, min_n_components=30, max_n_components=50):
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        time_windows, vocab, w2v = X
        dynamic_topics = DynamicTopics(time_windows, vocab, w2v, self.min_n_components, self.max_n_components)
        return time_windows, dynamic_topics

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