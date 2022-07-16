import os, pickle, warnings
from models.TimeWindow import TimeWindow
from models.Topic import Topic
from gensim.models import Word2Vec
from sklearn.decomposition import NMF

DATA_PATH = "data"

def fit_window_topics():
    # 1. Read time windows
    time_windows = [TimeWindow.load(DATA_PATH+"/"+f) for f in os.listdir("data") if f.endswith(".pkl") and not f.startswith("vocab")]
    # 2. Read w2v.model 
    w2v = Word2Vec.load(DATA_PATH+"/w2v.model")
    # 3. Read vocab
    with open('vocab.pkl', 'rb') as f:
        vocab = pickle.load(f)
    # 4. Fit window topics
    for time_window in time_windows:
        print(f"Fitting {time_window.id} ...")
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
        time_window.save(f"out/{time_window.id}.pkl")
        print(f"{time_window.id}: {time_window.n_titles} titles; {time_window.num_speeches} speeches; {time_window.num_topics} topics; {time_window.coherence} coherence;")

def main():
    fit_window_topics()
        
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
        print(f"k = {n_components}; coherence = {avg_coherence}")
    print(f"Best: k = {len(best_topics)}; coherence = {avg_coherence}")
    return best_topics, best_coherence

def fit_nmf(tfidf_matrix, n_components):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = NMF(n_components=n_components, init='nndsvd', solver='mu')
        w = model.fit_transform(tfidf_matrix)
        h = model.components_
    return w, h

if __name__ == "__main__":
    main()

