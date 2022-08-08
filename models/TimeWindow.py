import numpy as np
import pickle, logging
import pandas as pd
from scipy import spatial
from nmf import choose_topics
from sklearn.preprocessing import normalize

class TimeWindow:
    OUT_PATH = "out"

    def __init__(self, id, speech_ids, tfidf_matrix, vocab, alpha = 0.05, m = 40):
        self.id = id
        self.speech_ids = speech_ids
        self.tfidf_matrix = tfidf_matrix # TF-IDF of the time window
        self.vocab = vocab
        self.alpha = alpha
        self.m = m
        self.topics = [] # list of Topic
        self.coherence = 0
        self.children = []
        self.extras = []

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
            topic.id = f"{self.id}/{str(i).zfill(2)}"
        self.topics = topics
        self.coherence = coherence

        if self.id.count("/") == 0 and len(self.extra_speeches) > 0: # only applicable to root
            """
            self.fit_children(coherence_model, 5, 15)

            logger.info(f"Assign extra topics to leaf topic...")
            leaves = [self.topics[i] for i in self.leaf_topics]
            for child in self.children:
                leaves += child.topics
            for row in self.extra_speeches:
                speech_terms = self.tfidf_matrix.toarray()[row,:]
                best_topic = None
                best_similarity = 0
                for topic in leaves:
                    topic_terms = topic.term_weights
                    # cosine similiarity
                    similarity = 1 - spatial.distance.cosine(speech_terms, topic_terms)
                    if similarity > best_similarity:
                        best_topic = topic
                        best_similarity = similarity
                logger.info(f"extra: {self.speech_ids[row]}, {best_topic.id}, {best_similarity}")
                self.extras.append((self.speech_ids[row], best_topic.id, best_similarity))
            """
            logger.info(f"Fit extra topics...")
            extra_topics, extra_coherence = choose_topics(
                self.tfidf_matrix[self.extra_speeches], 
                self.vocab, 
                coherence_model, 
                min_n_components=min(2, len(self.extra_speeches)), 
                max_n_components=min(15, len(self.extra_speeches)),
            )
            for i, topic in enumerate(extra_topics):
                k = i + len(self.topics)
                topic.id = f"{self.id}/{str(k).zfill(2)}"
            self.extras = extra_topics
            # coherence = weighted average of topics and extras
            total = len(self.topics) + len(self.extras)
            self.coherence = self.coherence * len(self.topics) / total + extra_coherence * len(self.extras) / total

            self.save(f"{self.OUT_PATH}/{self.id}.pkl")
        
        logger.info(f"{self.id}: {self.num_speeches} speeches; {self.num_topics} topics; coherence = {self.coherence};")
        logger.info("-----------------------------------------------------------------------------")

    def fit_children(self, coherence_model, min_k, max_k):
        logger = logging.getLogger(__name__)
        logger.info(f">>> Fitting {self.id} children ...")

        popular_topics = self.popular_topics
        W = self.W[self.assigned_speeches]
        tf_idf = self.tfidf_matrix[self.assigned_speeches]
        speech_ids = self.speech_ids[self.assigned_speeches]
        x = np.argmax(W, axis=1)
        for pt in popular_topics:
            rows, *_ = np.where(x == pt)
            tfidf_matrix = normalize(tf_idf[rows], axis=1, norm='l2')
            child = TimeWindow(
                f"{self.id}/{str(pt).zfill(2)}",
                speech_ids[rows],
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
    def W_extra(self):
        return np.array([topic.document_weights for topic in self.extras]).T

    @property
    def extra_speeches(self):
        """
        speeches that can not be assigned to any topic, i.e. their correlation < alpha
        """
        max_weights = np.max(self.W, axis=1)
        nonzero, *_ = np.where(max_weights < self.alpha)
        return nonzero

    @property
    def assigned_speeches(self):
        """
        speeches that can be assigned to a topic, i.e. their correlation >= alpha
        """
        max_weights = np.max(self.W, axis=1)
        nonzero, *_ = np.asarray(max_weights >= self.alpha).nonzero()
        return nonzero

    @property
    def all_topics(self):
        """
        topics of this time windows & its children
        """
        topics = self.topics[:]
        for child in self.children:
            topics += child.all_topics
        return topics

    @property
    def all_leaves(self):
        """
        leaf topics of this time windows & its children
        """
        topics = [self.topics[i] for i in self.leaf_topics]
        for child in self.children:
            topics += child.all_leaves
        return topics

    @property
    def popular_topics(self):
        """
        topics that have more than m speeches assigned to
        return indices of those topics
        """
        rows = self.assigned_speeches
        W = self.W[rows]
        _, n_topics = W.shape
        x = np.argmax(W, axis=1)
        hist, _ = np.histogram(x, bins=range(n_topics+1))
        cols, *_ = np.where(hist > self.m)
        return cols
    
    @property
    def leaf_topics(self):
        """
        topics that have less than or equal to m speeches assigned to
        return index of those topics
        """
        rows = self.assigned_speeches
        W = self.W[rows]
        _, n_topics = W.shape
        x = np.argmax(W, axis=1)
        hist, _ = np.histogram(x, bins=range(n_topics+1))
        cols, *_ =  np.where(hist <= self.m)
        return cols

    @property
    def speech2topic(self):
        """
        Assuming a single membership model, i.e. each speech has 1 topic with the highest weight 
        """
        topics = np.argmax(self.W[self.assigned_speeches], axis=1)
        extras = np.argmax(self.W_extra, axis=1)
        temp = {j:i for i,j in enumerate(self.extra_speeches)}
        speech2topic = [(self.speech_ids[speech], self.topics[topic].id, self.W[speech, topic]) for speech, topic in zip(self.assigned_speeches, topics)]
        speech2extra = [(self.speech_ids[speech], self.extras[topic].id, self.W_extra[temp[speech], topic]) for speech, topic in zip(self.extra_speeches, extras)]
        #for child in self.children:
        #    speech2topic += child.speech2topic
        #speech2topic += self.extras
        return speech2topic + speech2extra

    def top_term_weights(self, n_top):
        """
        weight of top terms of all topics
        """
        return [topic.top_term_weights(n_top) for topic in self.topics]

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)