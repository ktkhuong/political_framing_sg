import spacy
from nltk.corpus import stopwords
from nltk import tokenize
from gensim.utils import simple_preprocess
import spacy
from tqdm import tqdm
from sklearn.base import BaseEstimator, TransformerMixin

###################################
#### stop words ####
###################################
stop_words = set(stopwords.words('english'))
extra_stop_words = {
    "please", "would", "use", "also", "thank", 
    # salutation
    "mr", "sir", "madam", "speaker", "minister", "member", "members", "honourable", 
    # parliamentary specific words
    "act", "amendment", "applause", "ask", "beg", "chair", "chairman", "clause", 
    "constitution", "laughter", "mentioned", "motion", "order", "ordinance", "party", "question", "regard", "report", "second", "sitting"
}
stop_words = stop_words.union(extra_stop_words)

class TokenizeSpeeches(BaseEstimator, TransformerMixin):
    def __init__(self, col):
        self.col = col
        self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X
        df["tokenized_speech"] = self.tokenize(df[self.col].values)        
        return df

    def tokenize(self, documents, batch_size=100, n_process=4):
        docs = [" ".join(
            self.remove_stopwords(
                self.sent2tokens(
                    self.doc2sent(
                        doc
                    )
                )
            )
        ) for doc in documents]
        lemmatized = [" ".join([token.lemma_ for token in doc]) for doc in tqdm(self.nlp.pipe(docs, batch_size=batch_size, n_process=n_process), total=len(docs))]
        return lemmatized

    def doc2sent(self, doc):
        return tokenize.sent_tokenize(doc)

    def sent2tokens(self, sentences):
        sent_tokens = [simple_preprocess(sentence, deacc=True) for sentence in sentences]
        return [token for tokens in sent_tokens for token in tokens]

    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in stop_words and len(token) > 2]

    def lemmatize(self, tokens):
        doc = self.nlp(" ".join(tokens))
        return [token.lemma_ for token in doc]

    