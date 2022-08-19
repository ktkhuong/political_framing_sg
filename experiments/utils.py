import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

def run_sql(path, sql):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows

def read_archive(path):
    path_csv = path + "sgparl_tokenized.csv"
    path_db = path + "sgparl.db"
    
    df = pd.read_csv(path_csv, usecols=["date", "quarter", "title", "member", "party", "preprocessed_speech"])
    df["date"] = pd.to_datetime(df['date'])
    df["word_count"] = df["preprocessed_speech"].map(lambda x: len(x.split()))
    
    rows = run_sql(
    path_db,
    """
    SELECT id, terms, coherence, speech2topic.speech
    FROM window_topics
    INNER JOIN speech2topic ON speech2topic.topic = window_topics.id
    """)
    df_speech2topic = pd.DataFrame(rows, columns=["window_topic_id", "window_topic_terms", "window_topic_coherence", "speech_id"]).reset_index(drop=True)
    df = df.merge(df_speech2topic, left_index=True, right_on="speech_id").reset_index(drop=True)
    
    rows = run_sql(
    path_db,
    """
    SELECT dynamic_topics.id, dynamic_topics.terms, dynamic_topics.coherence, window_topics.id
    FROM dynamic_topics
    INNER JOIN wt2dt on wt2dt.dynamic_topic = dynamic_topics.id
    INNER JOIN window_topics on wt2dt.window_topic = window_topics.id
    ORDER BY dynamic_topics.id
    """)
    df_dynamic = pd.DataFrame(rows, columns=["dynamic_topic_id", "dynamic_topic_terms", "dynamic_topic_coherence", "window_topic_id"])
    df = df.merge(df_dynamic, left_on="window_topic_id", right_on="window_topic_id").sort_values(by="speech_id")
        
    df = df[ ['speech_id'] + [ col for col in df.columns if col != 'speech_id' ] ]
    df = df.set_index("speech_id")
    return df

def find_dynamic_topic(df, i):
    df_table = df[df["dynamic_topic_id"] == i][["quarter", "window_topic_id","window_topic_terms",]].drop_duplicates().sort_values(by="window_topic_id").reset_index(drop=True)
    return df_table

def find_window_topic(df, i):
    df_table = df[df["window_topic_d"] == i][["quarter", "window_topic_id","window_topic_terms"]].drop_duplicates().sort_values(by="window_topic_id").reset_index(drop=True)
    return df_table
    
def to_puml(topics, terms):
    out = ""
    for i, (topic, words) in enumerate(zip(topics, terms)):
        out += f'object "{topic}" as o{i}\n'
        for word in words.split():
            out += f"o{i} : {word}\n"
    for i in range(1, len(topics)):
        out += f"o{i-1} --> o{i}\n"
    return out