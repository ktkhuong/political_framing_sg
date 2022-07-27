import os, pickle, warnings, logging, socket, getopt, sys, re
from models.TimeWindow import TimeWindow
from models.Topic import Topic
from gensim.models import Word2Vec
from read_dataset import speeches_from_json
import pandas as pd
from preprocess import preprocess_df
from models.CoherenceModel import Word2VecCoherenceModel, CvCoherenceModel
from optparse import OptionParser
from nmf import choose_topics
import numpy as np

DATA_PATH = "data"
OUT_PATH = "out"
DATASET_PATH = "dataset/parliament"

logging.basicConfig(
    format="%(asctime)s - %(funcName)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"out/{socket.gethostname()}.log"),
        logging.StreamHandler()
    ]
)

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
            min_n_components=min(min_k, time_window.num_speeches), 
            max_n_components=min(max_k, time_window.num_speeches),
        )
        for i, topic in enumerate(topics):
            topic.id = f"{time_window.id}/{i}"
        time_window.topics = topics
        time_window.coherence = coherence
        time_window.save(f"{OUT_PATH}/{time_window.id}.pkl")
        logger.info(f"{time_window.id}: {time_window.n_titles} titles; {time_window.num_speeches} speeches; {time_window.num_topics} topics; coherence = {time_window.coherence};")
        logger.info("-----------------------------------------------------------------------------")

    clear_dir(DATA_PATH)

def fit_subtopics(time_window: TimeWindow, vocab, coherence_model):
    logger = logging.getLogger(__name__)
    logger.info(f"Fitting subtopic of {time_window.id} ...")

    W = time_window.W
    n_docs, n_topics = W.shape
    logger.info(f"W shape:", W.shape)
    max_weights = np.max(W, axis=1)
    included = np.where(max_weights > 0.05)
    x = np.argmax(W, axis=1)
    hist, _ = np.histogram(x, bins=range(n_topics+1))
    for i, freq in enumerate(hist):
        if freq > 25:
            logger.info(f"fitting topic {i} freq = {freq}")
            rows = np.where(x == i)
            sub_window = TimeWindow(
                f"{time_window.id}/{i}",
                time_window.speech_ids[rows],
                time_window.tfidf_matrix[rows],
                0
            )
            topics, coherence = choose_topics(
                sub_window.tfidf_matrix, 
                vocab, 
                coherence_model, 
                min_n_components=min(10, time_window.num_speeches), 
                max_n_components=min(25, time_window.num_speeches),
            )
            for j, topic in enumerate(topics):
                topic.id = f"{time_window.id}/{i}/{j}"
            sub_window.topics = topics
            sub_window.coherence = coherence
            logger.info(f"{sub_window.id}: {sub_window.num_speeches} speeches; {sub_window.num_topics} topics; coherence = {sub_window.coherence};")
            time_window.sub_windows.append(sub_window)            

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
    

if __name__ == "__main__":
    main()