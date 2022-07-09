import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from itertools import combinations
from scipy import spatial
from gensim.models import Word2Vec
import pickle
from glove import Glove
import logging

class Topic:
    N_TOP_TERMS = 10

    def __init__(self, term_weights, document_weights, vocab):
        self.term_weights = term_weights
        self.document_weights = document_weights
        self.vocab = vocab

    def top_term_indices(self, n_top=N_TOP_TERMS):
        return np.argsort(self.term_weights)[::-1][:n_top]

    def top_terms(self, n_top=N_TOP_TERMS):
        top_indices = self.top_term_indices(n_top)
        return [self.vocab[i] for i in top_indices]

    def coherence_w2v(self, w2v):
        top_terms = self.top_terms()
        total_distance = 0
        count = 0
        for wi, wj in combinations(top_terms, 2):
            total_distance += w2v.wv.similarity(wi, wj)
            count += 1
        return float(total_distance) / (count)

    def coherence_glove(self, glove):
        top_terms = self.top_terms()
        total_distance = 0
        count = 0
        for wi, wj in combinations(top_terms, 2):
            assert wi in glove.wv.keys(), f"{wi} NOT found in glove"
            assert wj in glove.wv.keys(), f"{wj} NOT found in glove"
            total_distance += 1 - spatial.distance.cosine(glove.wv[wi], glove.wv[wj])
            count += 1
        return float(total_distance) / (count)

class TwoLayersNMF:
    N_COHERENCE_WORDS = 10
    N_DYNAMIC_TOP_TERMS = 20

    @classmethod
    def by_w2v(cls, tokenized):
        instance = cls(tokenized)
        instance.word_embeddings = TwoLayersNMF.train_word2vec
        instance.get_coherence = Topic.coherence_w2v
        return instance

    @classmethod
    def by_glove(cls, tokenized):
        raise NotImplementedError()
        """
        instance = cls(tokenized)
        instance.word_embeddings = TwoLayersNMF.train_glove
        instance.get_coherence = Topic.coherence_glove
        return instance
        """

    def __init__(self, tokenized):
        tfidf = self.train_tfidf(tokenized)
        #self.index_to_word = vocab
        #self.word_to_index = {w: i for i, w in enumerate(vocab)}

        #self.n_words = len(vocab)
        self.window_topics = []
        self.dynamic_topics = []

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    #def fit(self, windows):
    def fit(self):
        logger = logging.getLogger(__name__)
        # 1. TFIDF
        #logger.info("Fitting TF-IDF")
        #tfidf = self.train_tfidf()
        # 2. Compute word embeddings
        #self.word_embeddings()

        #self.windows = windows
        #self._fit_window_topics()
        #self._fit_dynamic_topics()

    def _fit_window_topics(self):
        window_topics = []
        for i, window in enumerate(self.windows):
            window_topics.append(self._choose_topics(window, self.index_to_word))

        self.window_topics = window_topics

    def _fit_dynamic_topics(self, n_top=N_DYNAMIC_TOP_TERMS):
        rows = []
        for topics in self.window_topics:
            for topic in topics:
                row = np.zeros((self.n_words,))

                top_word_index = [
                    self.word_to_index[word]
                    for word in topic.top_terms(n_top)
                ]

                row[top_word_index] = topic.term_weights[top_word_index]
                rows.append(row)

        stacked = np.vstack(rows)

        keep_terms = stacked.sum(axis=0) != 0
        keep_term_names = np.array(self.index_to_word)[keep_terms]

        reduced = stacked[:,keep_terms]
        normalized = normalize(reduced, axis=1, norm='l2')

        self.dynamic_topics = self._choose_topics(
            normalized,
            keep_term_names,
            min_n_components=30,
            max_n_components=50)

    def _choose_topics(self, vectors, vocab, min_n_components=10, max_n_components=25):
        best_coherence = float('-inf')
        best_topics = None

        coherences = []
        for n_components in range(min_n_components, max_n_components + 1):
            w,h = self.train_nmf(vectors, n_components)
            topics = [Topic(term_weights, doc_weights, vocab) for term_weights, doc_weights in zip(h, w.T)]

            avg_coherence = (
                sum(self.get_coherence(t, self.word_vectors) for t in topics) /
                len(topics))

            coherences.append(avg_coherence)

            if avg_coherence > best_coherence:
                best_coherence = avg_coherence
                best_topics = topics

        return best_topics

    @staticmethod
    def train_nmf(data, n_components):
        model = NMF(n_components=n_components, init='nndsvd')
        w = model.fit_transform(data)
        h = model.components_
        return w,h

    @staticmethod
    def train_tfidf(self, documents, max_df=0.2, min_df=5):
        tfidf = TfidfVectorizer(norm='l2', max_df=max_df, min_df=min_df)
        tfidf.fit(documents)
        return tfidf

    @staticmethod
    def train_glove(self, tokenized):
        raise NotImplementedError()
        """
        glove = Glove()
        docs = [' '.join(tokens) for tokens in tokenized]
        return glove.fit(docs)
        """

    def train_word2vec(self, tokenized):
        w2v = Word2Vec(tokenized, min_count=1)
        return w2v