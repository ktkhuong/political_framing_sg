from unidecode import unidecode
import os, json
import datetime
import logging

def format_date(date):
    day, month, year = list(map(int, date.split("-")))
    return datetime.datetime(year, month, day).strftime("%Y-%m-%d")

def get_quarter(date):
    day, month, year = list(map(int, date.split("-")))
    return f"{year}Q{(month-1)//3+1}"
                                  
def speeches_from_json(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    logging.info(f"read {json_file}")
    return [{
        #"file": json_file.split("/")[-1],
        "section": data["section"], 
        "date": format_date(data["date"]),
        "quarter": get_quarter(data["date"]),
        "title": data["title"],
        "member": unidecode(speech["name"] or ''),
        "speech": unidecode(speech["speech"] or ''),
    } for speech in data["speeches"]]