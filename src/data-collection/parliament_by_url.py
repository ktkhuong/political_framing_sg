from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from database import Database
import os
import getopt, sys
import re
import json

def main():
    url = None
    parliament_number = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:")
        for opt, arg in opts:
            if opt == '-u':
                url = arg
            elif opt == '-p':
                parliament_number = arg
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        quit()

    driver = webdriver.Chrome(service=Service("chromedriver.exe"))
    driver.get(url)

    db = Database('parliament.db', 'parliament')

    match = re.search(r"reportid=.*", driver.current_url)
    id = match.group()[9:]
    path = f"parliament\\{parliament_number}\\{id}.json"
    
    try:
        section = ''
        rows = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table tr')))
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                info_type, info = cells
                if info_type.text.lower() == "section name:":
                    section = info.text

        content = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="showTopic"]/div')))
        meta_info = driver.find_elements(By.CSS_SELECTOR, "table[border='1'] tr tr")
        title_text = meta_info[6].text[6:].strip()
        sitting_date_text = meta_info[4].text[13:].strip()
        # remove noise text
        driver.execute_script("""
            document.querySelector("table[border='1']")?.remove();
            document.querySelector(".hansardcustom table")?.remove();
            document.querySelectorAll("b,strong").forEach((element) => {
                if (element.innerText.startsWith("Column: ")) {
                    element.remove();
                }
                else {
                    element.innerText = "#" + element.innerText + "#";
                }
            });
            document.querySelectorAll("p[align='left']").forEach((element) => {
                if (element.innerText.startsWith("Column: ")) {
                    element.remove();
                }
            });
            document.querySelectorAll("div[align='center']").forEach((element) => {
                element.remove();
            });
        """)
        text = content.text
        text = "".join([re.sub(r"^1[0-2]|0?[1-9].[0-5]?[0-9] ?[ap].m.$", "", line.strip(), flags=re.IGNORECASE) 
                            for line in text.splitlines() if line.strip()])
        speaker_loc = [speaker.span() for speaker in re.finditer("#(.*?)#", text)]
        if (len(speaker_loc) == 0):
            with open(f"{path}", "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": id,
                    "section": section,
                    "title": title_text,
                    "date": sitting_date_text,
                    "speeches": [{
                        "name": None, 
                        "speech": text
                    }],
                }))
            db.save_record(sitting_date_text, title_text, driver.current_url, path)
        else:
            speaker_starts, speaker_ends = list(zip(*speaker_loc))
            speech_text_starts = speaker_ends[:]
            speech_text_ends = speaker_starts[1:] + (-1,)
            speeches_loc = list(zip(speaker_starts, speaker_ends, speech_text_starts, speech_text_ends))
            speeches = {
                "id": id,
                "section": section,
                "title": title_text,
                "date": sitting_date_text,
                "speeches": [
                {
                    "name": text[name_start+1:name_end-1], 
                    "speech": text[speech_text_start+1:(speech_text_end if speech_text_end != -1 else None)]
                } for (name_start, name_end, speech_text_start, speech_text_end) in speeches_loc
            ]}
            with open(f"{path}", "w", encoding="utf-8") as f:
                f.write(json.dumps(speeches))
            db.save_record(sitting_date_text, title_text, driver.current_url, path)
    except Exception as e:
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(f"{driver.current_url} {path}: {str(e)}\n")

if __name__ == "__main__":
    main()