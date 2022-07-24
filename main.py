import os, pickle, warnings, logging, socket, getopt, sys, re
from models.TimeWindow import TimeWindow
from models.Topic import Topic
from gensim.models import Word2Vec
from sklearn.decomposition import NMF
from read_dataset import speeches_from_json
import pandas as pd
from preprocess import preprocess_df
from models.CoherenceModel import Word2VecCoherenceModel, CvCoherenceModel
from optparse import OptionParser

DATA_PATH = "data"
OUT_PATH = "out"
DATASET_PATH = "dataset/parliament"

def clear_dir(path):
    for f in os.listdir(path):
        fp = f"{path}/{f}"
        os.remove(fp)

def fit_window_topics(min_k=10, max_k=25):
    logger = logging.getLogger(__name__)

    clear_dir(OUT_PATH)

    # 1. Read time windows
    time_windows = [TimeWindow.load(DATA_PATH+"/"+f) for f in os.listdir("data") if f.endswith(".pkl") and not f.startswith("vocab")]
    # 2. Read coherence_model.model 
    if os.path.exists(DATA_PATH+"/w2v.model"):
        logger.info("using Word2VecCoherenceModel")
        coherence_model = Word2VecCoherenceModel.load(DATA_PATH+"/w2v.model")
    elif os.path.exists(DATA_PATH+"/cv.model"):
        logger.info("using CvCoherenceModel")
        coherence_model = CvCoherenceModel.load(DATA_PATH+"/cv.model")
    else:
        raise RuntimeError("Coherence model NOT found!")
    # 3. Read vocab
    with open(DATA_PATH+'/vocab.pkl', 'rb') as f:
        vocab = pickle.load(f)
    # 4. Fit window topics
    for time_window in time_windows:
        logger.info(f"Fitting {time_window.id} ...")
        topics, coherence = choose_topics(
            time_window.tfidf_matrix, 
            vocab, 
            coherence_model, 
            min_n_components=min_k, 
            max_n_components=max_k,
        )
        for i, topic in enumerate(topics):
            topic.id = f"{time_window.id}/{i}"
        time_window.topics = topics
        time_window.coherence = coherence
        time_window.save(f"{OUT_PATH}/{time_window.id}.pkl")
        logger.info(f"{time_window.id}: {time_window.n_titles} titles; {time_window.num_speeches} speeches; {time_window.num_topics} topics; coherence = {time_window.coherence};")
        logger.info("-----------------------------------------------------------------------------")

    clear_dir(DATA_PATH)

def preprocess(parl_num):
    logger = logging.getLogger(__name__)

    path = f"{DATASET_PATH}/{parl_num}"
    records = [speech for f in os.listdir(path) if f.lower().endswith(".json") 
                      for speech in speeches_from_json(f"{path}/{f}")]
    with open(f"{DATASET_PATH}/mp.txt") as f:
        members = [re.sub(r"[^a-z. ]", "", line.replace("\n","").lower().strip()) for line in f.readlines() if line.strip()]
    df = pd.DataFrame.from_records(records)
    df['date'] = pd.to_datetime(df['date'])
    df_members = pd.DataFrame(members, columns=["name"])
    df_members = df_members.drop_duplicates(["name"]).reset_index(drop=True)
    df = preprocess_df(df, df_members['name'].values)
    df.to_csv(f"{OUT_PATH}/parliament_{parl_num}.csv")
    logger.info(f"Data frame: {df.shape}")

def main():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-f", "--fit", action="store_true", dest="run_fit", help="fit window topics")
    parser.add_option("-k", "--num-topics", action="store", type="string", dest="num_topics", help="range of number of topics, comma separated", default="10,25")
    parser.add_option("-p", "--preprocess", action="store_true", dest="run_preprocess", help="preprocess data")
    parser.add_option("-n", "--parlnum", action="store", type=int, dest="parl_num", help="number of available virtual machines", default=1)
    (options, args) = parser.parse_args()
    if options.run_fit == None and options.run_preprocess == None:
        parser.error("Must specify either -f or -p to dataset")

    if options.run_fit:
        logging.basicConfig(
            format="%(asctime)s - %(funcName)s - %(message)s", 
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"out/{socket.gethostname()}_fit.log"),
                logging.StreamHandler()
            ]
        )
        min_k, max_k = list(map(int, options.num_topics.split(",")))
        fit_window_topics(min_k, max_k)
    elif options.run_preprocess:
        logging.basicConfig(
            format="%(asctime)s - %(funcName)s - %(message)s", 
            level=logging.INFO,
            handlers=[
                logging.FileHandler(f"out/{socket.gethostname()}_preprocess.log"),
                logging.StreamHandler()
            ]
        )
        preprocess(options.parl_num)
        
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
        logger.info(f"k = {n_components}; coherence = {avg_coherence}")
    logger.info(f"Best: k = {len(best_topics)}; coherence = {best_coherence}")
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