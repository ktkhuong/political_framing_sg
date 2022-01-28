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
import re
import json
import os

class Parliament:
    def __init__(self, path: str, driver: webdriver.Chrome) -> None:
        self.path = path
        self.driver = driver

    def extract_data(self, on_done):
        self.switch_to_tab()
        self.enumerate_pages()
        self.close_tab()
        on_done()

    def close_tab(self):
        pass

    def switch_to_tab(self):
        *_, search_results = self.driver.window_handles
        self.driver.switch_to.window(search_results)
        sleep(1)        

    def enumerate_pages(self):
        last_page = False
        while last_page is False:
            try:
                self.enumerate_reports()
                self.scroll_to_bot()
                next_page = self.driver.find_element(By.CLASS_NAME, 'fa.fa-angle-right')
                next_page.click()
            except NoSuchElementException:
                last_page = True

    def enumerate_reports(self):
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchResults"]/table/*')))
            results_table = self.driver.find_element(By.XPATH, '//*[@id="searchResults"]/table')
            tbodies = results_table.find_elements(By.TAG_NAME, "tbody")
            for tbody in tbodies:
                self.save_report(tbody)
        except TimeoutException:
            pass

    def save_report(self, tbody):
        title_row, sitting_date_row = tbody.find_elements(By.TAG_NAME, "tr")
        title_link = title_row.find_element(By.TAG_NAME, "a")
        date_em, *_ = sitting_date_row.find_elements(By.TAG_NAME, "em")
        title_text = title_link.text
        illegal_characters_removed = re.sub(r'[^A-Za-z0-9 ]+', '', title_text)
        sitting_date_text = date_em.text[-10:-1] # example: Sitting Date: 24-1-1968,
        filename = f"{sitting_date_text} {illegal_characters_removed[:50]}.json"

        path = f"{self.path}\\{filename}"
        if os.path.exists(path):
            with open("errors.log", "a", encoding="utf-8") as f:
                f.write(f"{path} exists \n")
            return

        self.driver.execute_script("arguments[0].scrollIntoView();", title_link)
        sleep(1)
        title_link.click()
        sleep(0.5)
        *_, search_results, report = self.driver.window_handles
        self.driver.switch_to.window(report)

        try:
            content = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="showTopic"]/div')))
            # remove noise text
            self.driver.execute_script("""
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
                        "name": None,
                        "speech": text
                    }))
            else:
                speaker_starts, speaker_ends = list(zip(*speaker_loc))
                speech_text_starts = speaker_ends[:]
                speech_text_ends = speaker_starts[1:] + (-1,)
                speeches_loc = list(zip(speaker_starts, speaker_ends, speech_text_starts, speech_text_ends))
                speeches = {
                    "title": title_text,
                    "data": sitting_date_text,
                    "speeches": [
                    {
                        "name": text[name_start+1:name_end-1], 
                        "speech": text[speech_text_start+1:(speech_text_end if speech_text_end != -1 else None)]
                    } for (name_start, name_end, speech_text_start, speech_text_end) in speeches_loc
                ]}
                with open(f"{path}", "w", encoding="utf-8") as f:
                    f.write(json.dumps(speeches))
        except Exception as e:
            with open("errors.log", "a", encoding="utf-8") as f:
                f.write(f"{sitting_date_text} {title_text}: {str(e)}\n")

        self.driver.close()
        self.driver.switch_to.window(search_results)

    def scroll_to_bot(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
