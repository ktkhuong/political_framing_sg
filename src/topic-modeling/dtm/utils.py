import pandas as pd

def to_date(df_input, col_date, date_in_str):
    return df_input[df_input[col_date] <= pd.Timestamp(date_in_str)]

def from_date(df_input, col_date, date_in_str):
    return df_input[df_input[col_date] >= pd.Timestamp(date_in_str)]