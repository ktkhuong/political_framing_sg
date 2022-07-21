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
        #data = {topic.id: " ".join(topic.top_terms()) for time_window in time_windows for topic in time_window.topics}
        data = defaultdict(list)
        for time_window in time_windows:
            for topic in time_window.topics:
                data['id'].append(topic.id)
                data['topic'].append(" ".join(topic.top_terms()))
                data['coherence'].append(topic.coherence)
        df_window_topics = pd.DataFrame.from_dict(data).set_index("id")
        df_window_topics.to_sql(name=self.TABLE_WINDOW_TOPICS, con=conn)
        conn.close()

    def save_speech2topic(self, time_windows):
        conn = sqlite3.connect(self.db_name)
        speech2topic = {}
        for time_window in time_windows:
            speech2topic = {**speech2topic, **time_window.speech2topic}
        df_speech2topic = pd.DataFrame(speech2topic.items(), columns=["speech","topic"]).set_index("speech")
        df_speech2topic.to_sql(name=self.TABLE_SPEECH_2_TOPIC, con=conn)
        conn.close()

    def save_dynamic_topics(self, dynamic_topics):
        conn = sqlite3.connect(self.db_name)
        #data = {i: " ".join(topic.top_terms()) for i, topic in enumerate(dynamic_topics.topics)}
        data = defaultdict(list)
        for i, topic in enumerate(dynamic_topics.topics):
            data['id'].append(i)
            data['topic'].append(" ".join(topic.top_terms()))
            data['coherence'].append(topic.coherence)
        df_dynamic_topics = pd.DataFrame.from_dict(data).set_index("id")
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