import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import sqlite3
from collections import defaultdict

class SaveToDb(BaseEstimator, TransformerMixin):
    TABLE_WINDOW_TOPICS = "window_topics"
    TABLE_SPEECH_2_TOPIC = "speech2topic"
    TABLE_DYNAMIC_TOPICS = "dynamic_topics"
    TABLE_WINDOW_TOPIC_2_DYNAMIC_TOPIC = "wt2dt"

    def __init__(self, db_name="sgparl.db"):
        self.db_name = db_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        self.save_window_topics(X.time_windows)
        self.save_speech2topic(X.time_windows)
        self.save_dynamic_topics(X)
        self.save_wt2dt(X)
        return X

    def save_window_topics(self, time_windows):
        conn = sqlite3.connect(self.db_name)
        data = [(topic.id, " ".join(topic.top_terms()), topic.coherence, ",".join(map(str, topic.term_weights[topic.top_term_indices()]))) for time_window in time_windows for topic in time_window.topics]
        df_window_topics = pd.DataFrame(data, columns=["id","terms","coherence", "term_weights"]).set_index("id")
        df_window_topics.to_sql(name=self.TABLE_WINDOW_TOPICS, con=conn)
        conn.close()

    def save_speech2topic(self, time_windows):
        conn = sqlite3.connect(self.db_name)
        speech2topic = []
        for time_window in time_windows:
            speech2topic += time_window.speech2topic
        df_speech2topic = pd.DataFrame(speech2topic, columns=["speech","topic","weight"])
        df_speech2topic.to_sql(name=self.TABLE_SPEECH_2_TOPIC, con=conn)
        conn.close()

    def save_dynamic_topics(self, dynamic_topics):
        dynamic_topics.save("dtm.pkl")
        conn = sqlite3.connect(self.db_name)
        data = [(i, " ".join(topic.top_terms()), topic.coherence, ",".join(map(str, topic.term_weights[topic.top_term_indices()]))) for i, topic in enumerate(dynamic_topics.topics)]
        df_dynamic_topics = pd.DataFrame(data, columns=["id","terms","coherence", "term_weights"]).set_index("id")
        df_dynamic_topics.to_sql(name=self.TABLE_DYNAMIC_TOPICS, con=conn)
        conn.close()

    def save_wt2dt(self, dynamic_topics):
        conn = sqlite3.connect(self.db_name)

        data = {}
        offset = 0
        wt2dt = dynamic_topics.wt2dt
        for time_window in dynamic_topics.time_windows:
            for i, topic in enumerate(time_window.topics):
                data[topic.id] = wt2dt[i+offset]
            offset += len(time_window.topics)
        df_wt2dt = pd.DataFrame(data.items(), columns=["window_topic", "dynamic_topic"])
        df_wt2dt.to_sql(name=self.TABLE_WINDOW_TOPIC_2_DYNAMIC_TOPIC, con=conn)

        conn.close()