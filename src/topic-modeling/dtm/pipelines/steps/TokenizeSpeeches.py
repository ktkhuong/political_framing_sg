import spacy
from nltk import tokenize
from gensim.utils import simple_preprocess
import spacy
from tqdm import tqdm
from sklearn.base import BaseEstimator, TransformerMixin

###################################
#### stop words ####
###################################
def load_stopwords(path="stopwords.txt" ):
	"""
	Load stopwords from a file into a set.
	"""
	stopwords = set()
	with open(path) as f:
		lines = f.readlines()
		for l in lines:
			l = l.strip()
			if len(l) > 0:
				stopwords.add(l)
	return stopwords
stop_words = load_stopwords()
extra_stop_words = {
    "please", "would", "use", "also", "thank", 
    # salutation
    "mr", "sir", "madam", "speaker", "minister", "member", "members", "honourable", 
    # parliamentary related stop-words
    "bill", "ministry", "parliament",
    "act", "amendment", "applause", "ask", "beg", "chair", "chairman", "clause", 
    "constitution", "laughter", "mentioned", "motion", "order", "ordinance", "party", "question", "regard", "report", "second", "sitting",
    # others
    "singapore", "government", "singaporean",
}
stop_words = stop_words.union(extra_stop_words)

class TokenizeSpeeches(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        assert "preprocessed_speech" in df.columns, ""
        df["tokenized_speech"] = self.tokenize(df["preprocessed_speech"].values) 
        return df

    def tokenize(self, documents, batch_size=100, n_process=4, allowed_postags=['NOUN']):
        docs = [" ".join(
            self.sent2tokens(
                self.doc2sent(
                    doc
                )
            )
        ) for doc in documents]
        lemmatized = [" ".join([token.lemma_ for token in doc if token.pos_ in allowed_postags and token.lemma_ not in stop_words]) for doc in tqdm(
            self.nlp.pipe(docs, batch_size=batch_size, n_process=n_process), 
            total=len(docs),
            )]
        return lemmatized

    def doc2sent(self, doc):
        return tokenize.sent_tokenize(doc)

    def sent2tokens(self, sentences):
        sent_tokens = [simple_preprocess(sentence, deacc=True, min_len=3) for sentence in sentences]
        return [token for tokens in sent_tokens for token in tokens]

    