import logging, warnings
from models.Topic import Topic
from sklearn.decomposition import NMF

def choose_topics(tfidf_matrix, vocab, coherence_model, min_n_components=10, max_n_components=25):
    logger = logging.getLogger(__name__)

    best_coherence = float('-inf')
    best_topics = None
    coherences = []
    for n_components in range(min_n_components, max_n_components+1):
        w, h = fit_nmf(tfidf_matrix, n_components)
        topics = [Topic(term_weights, doc_weights, vocab) for term_weights, doc_weights in zip(h, w.T)]

        avg_coherence = sum(coherence_model.compute_coherence(topic) for topic in topics) / len(topics)
        coherences.append(avg_coherence)
        if avg_coherence > best_coherence:
            best_coherence = avg_coherence
            best_topics = topics
        logger.message(f"k = {n_components}; coherence = {avg_coherence}")
    logger.message(f"Best: k = {len(best_topics)}; coherence = {best_coherence}")
    return best_topics, best_coherence

def fit_nmf(tfidf_matrix, n_components):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = NMF(n_components=n_components, init='nndsvd', solver='mu')
        w = model.fit_transform(tfidf_matrix)
        h = model.components_
    return w, h