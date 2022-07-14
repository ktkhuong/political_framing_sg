import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import sqlite3
import logging

class SaveDynamicTopicsToDb(BaseEstimator, TransformerMixin):
    TABLE_TOPICS = "dynamic_topics"
    TABLE_WINDOW_TOPIC_2_DYNAMIC_TOPIC = "wt2dt"

    def __init__(self, db_name="sgparl.db"):
        self.db_name = db_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        time_windows, dynamic_topics = X
        self.save_dynamic_topics(dynamic_topics)
        self.save_wt2dt(time_windows, dynamic_topics)
        return X

    def save_dynamic_topics(self, dynamic_topics):
        conn = sqlite3.connect(self.db_name)

        data = {i: " ".join(topic.top_terms()) for i, topic in enumerate(dynamic_topics.topics)}
        df_dynamic_topics = pd.DataFrame(data.items(), columns=["id","topic"]).set_index("id")
        df_dynamic_topics.to_sql(name=self.TABLE_TOPICS, con=conn)

        conn.close()

    def save_wt2dt(self, time_windows, dynamic_topics):
        conn = sqlite3.connect(self.db_name)

        data = {}
        offset = 0
        wt2dt = dynamic_topics.wt2dt
        for time_window in time_windows:
            for i, topic in enumerate(time_window.topics):
                data[topic.id] = wt2dt[i+offset]
            offset += len(time_window.topics)
        df_wt2dt = pd.DataFrame(data.items(), columns=["window_topic", "dynamic_topic"])
        df_wt2dt.to_sql(name=self.TABLE_WINDOW_TOPIC_2_DYNAMIC_TOPIC, con=conn)

        conn.close()


        
        