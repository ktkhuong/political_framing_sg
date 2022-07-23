from itertools import combinations
import numpy as np
from gensim.models import Word2Vec

class Topic:
    N_TOP_TERMS = 10

    def __init__(self, term_weights, document_weights, vocab):
        self.term_weights = term_weights
        self.document_weights = document_weights
        self.vocab = vocab
        self.id = None
        self.coherence = 0

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