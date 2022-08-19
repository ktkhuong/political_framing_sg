from abc import ABC, abstractmethod
from models.Topic import Topic
from itertools import combinations
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary
from gensim.models import Word2Vec
import pickle

class BaseCoherenceModel(ABC):
    @abstractmethod
    def compute_coherence(self, topic, n_terms=Topic.N_TOP_TERMS):
        raise NotImplementedError()

    @abstractmethod
    def save(self, path):
        raise NotImplementedError()

class Word2VecCoherenceModel(BaseCoherenceModel):
    def __init__(self, w2v: Word2Vec):
        self.w2v = w2v

    def compute_coherence(self, topic: Topic, n_terms=Topic.N_TOP_TERMS):
        comb = list(combinations(topic.top_terms(n_terms), 2))
        total_distance = sum(self.w2v.wv.similarity(wi, wj) for wi, wj in comb)
        topic.coherence = float(total_distance) / len(comb)
        return topic.coherence

    def save(self, path):
        self.w2v.save(path)

    @staticmethod
    def load(path):
        return Word2VecCoherenceModel(Word2Vec.load(path))

class CvCoherenceModel(BaseCoherenceModel):
    def __init__(self, corpus, dictionary: Dictionary):
        self.corpus = corpus
        self.dictionary = dictionary

    def compute_coherence(self, topic: Topic, n_terms=Topic.N_TOP_TERMS):
        cm = CoherenceModel(topics=topic.top_terms(n_terms), texts=self.corpus, dictionary=self.dictionary, coherence='c_v')
        topic.coherence = cm.get_coherence()
        return topic.coherence

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)