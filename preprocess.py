import re
import pandas as pd

###################################
#### speech level preprocess ####
###################################

# lowercase + base filter
# some normalization
def preprocess_speech(speech):
    # remove names, must be done before lowering case
    speech = re.sub(r"(Mr|Mdm|Ms|Miss|Mrs|Dr\.|Dr|Madam|(Assoc )?Prof|Minister)( \b[A-Z].*?\b)+(,|'s)?", '', speech)
    # lowercase
    speech = speech.lower()
    # letter repetition (if more than 2)
    speech = re.sub(r'([a-z])\1{2,}', r'\1', speech)
    # non-word repetition (if more than 1)
    speech = re.sub(r'([\W+])\1{1,}', r'\1', speech)
    # combine hyphenated words
    speech = re.sub(r'((?:\w+-)+\w+)', lambda x: ''.join(x.group().split('-')), speech)
    # remove "'s"
    speech = re.sub(r"'s ", ' ', speech)
    # stuff in parenthesis, assumed to be less informal
    speech = re.sub(r'\(.*?\)', '', speech)
    # similarly for square brackets []
    speech = re.sub(r'\[.*?\]', '', speech)
    # double quotes and backward slash
    speech = re.sub(r'".*?"', lambda x: x.group()[1:-1], speech)
    speech = re.sub(r'\\.*?\\', lambda x: x.group()[1:-1], speech)
    # noise text: time
    speech = re.sub(r"([12])?[0-9]\.([0-5][0-9]) [ap]m", "", speech)
    # noise text at the beginning, followed by ":"
    speech = re.sub(r"^.*?:", lambda x: x.group() if re.search(r"[,.]", x.group()) else "", speech)
    # noise text: (mr|mdm) speaker
    speech = re.sub(r"(madam|mr|mdm) (deputy )?(speaker|chairman)", "", speech)
    # noise text: "madam,", "sir,"
    speech = re.sub(r"(,|\.) (madam|sir)(,|\.) ", " ", speech)
    speech = re.sub(r"^(madam|sir), ", "", speech)
    # noise text
    speech = re.sub(r"column:\d+", "", speech)
    # non-word standing alone
    speech = re.sub(r' \W ', " ", speech)
    # non-words at the beginning
    speech = re.sub(r"^\W+", "", speech)
    # multiple spaces
    speech = re.sub(r"^\s*|\s\s*", " ", speech)
    # strip white spaces at the beginning & end
    return speech.strip()

###################################
#### data frame level preprocess ##
###################################
def lowercase(df_input, cols):
    df_copy = df_input.copy()
    for c in cols:
        df_copy[c] = df_copy[c].str.lower()
    return df_copy

def drop_empty(df_input, cols) -> pd.DataFrame:
    for c in cols:
        df_input = df_input[df_input[c] != ""]
    return df_input

def preprocess_section(s):
    # only alphabets and dot
    s = re.sub(r"[^a-z. ]", "", s)
    # merging
    s = 'answers to questions' if re.search(r"answer(s?) to question(s?)", s) else s
    s = 'motions' if re.search(r"motion(s?)", s) else s
    s = 'bills' if re.search(r"bill(s?)", s) else s
    return s

def preprocess_members(df_input, members):
    def name_or_empty(text, names):
        for name in names:
            if name in text:
                return name
        return "unidentifiable"
    df_input['member'] = df_input['member'].map(lambda text: name_or_empty(text, members))
    df_input = drop_empty(df_input, ["member"])
    return df_input

def preprocess_df(df_input, members):
    # drop rows where member is empty
    df_input = drop_empty(df_input, ["member"])
    
    # lowercase
    df_input = lowercase(df_input, ["section", "title", "member"])
    
    # 'member' only accept alpha numeric characters
    df_input['member'] = df_input['member'].map(lambda text: re.sub(r"[^a-z. ]", "", text))    
    # Prime Ministers was sometimes referred to as "the prime minister" instead of their names. We have to replace these by their names:
    # lee kuan yew: 1959-06-05 to 1990-11-28
    # goh chok tong: 1990-11-28 to 2004-08-12
    # lee hsien loong: 2004-08-12 to present
    df_input.loc[(df_input['member'] == "the prime minister") & (df_input['date'] < pd.Timestamp(1990, 11, 28)), "member"] = 'lee kuan yew'    
    df_input.loc[(df_input['member'] == "the prime minister") & (df_input['date'] >= pd.Timestamp(1990, 11, 28)) & (df_input['date'] < pd.Timestamp(2004, 8, 12)), "member"] = 'goh chok tong'
    df_input.loc[(df_input['member'] == "the prime minister") & (df_input['date'] >= pd.Timestamp(2004, 8, 12)), "member"] = 'lee hsien loong'
    
    # reduce the number of sections by merging some of them
    df_input['section'] = df_input['section'].map(preprocess_section)
    # convert 'section' from string to category
    df_input["section"] = df_input["section"].astype("category")
    
    # preprocess speech
    df_input['preprocessed_speech'] = df_input['speech'].map(preprocess_speech)
    # drop empty preprocessed_speech
    df_input = drop_empty(df_input, ["preprocessed_speech"])
    # drop duplicated preprocessed_speech
    df_input = df_input.drop_duplicates(subset=['preprocessed_speech'])

    # preprocess members
    df_input = preprocess_members(df_input, members)

    return df_input