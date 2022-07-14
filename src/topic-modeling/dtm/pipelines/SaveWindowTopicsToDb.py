import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import sqlite3

class SaveWindowTopicsToDb(BaseEstimator, TransformerMixin):
    TABLE_TOPICS = "window_topics"
    TABLE_SPEECH_2_TOPIC = "speech2topic"

    def __init__(self, db_name="sgparl.db"):
        self.db_name = db_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        time_windows, *_ = X
        self.save_topics(time_windows)
        self.save_speech2topic(time_windows)
        return X

    def save_topics(self, time_windows):
        conn = sqlite3.connect(self.db_name)
        data = {topic.id: " ".join(topic.top_terms()) for time_window in time_windows for topic in time_window.topics}
        df_window_topics = pd.DataFrame(data.items(), columns=["id","topic"]).set_index("id")
        df_window_topics.to_sql(name=self.TABLE_TOPICS, con=conn)
        conn.close()

    def save_speech2topic(self, time_windows):
        conn = sqlite3.connect(self.db_name)
        speech2topic = {}
        for time_window in time_windows:
            speech2topic = {**speech2topic, **time_window.speech2topic}
        df_speech2topic = pd.DataFrame(speech2topic.items(), columns=["speech","topic"]).set_index("speech")
        df_speech2topic.to_sql(name=self.TABLE_SPEECH_2_TOPIC, con=conn)
        conn.close()