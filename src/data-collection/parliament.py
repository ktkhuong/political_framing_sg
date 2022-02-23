
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
from unidecode import unidecode
import os
import getopt, sys
import re
import json

class Parliament:
    def __init__(self, path: str, driver: webdriver.Chrome) -> None:
        self.path = path
        self.driver = driver
        self.db = Database('parliament.db', 'parliament') 

    def extract_data(self):
        self.switch_to_tab()
        self.enumerate_pages()
        self.close_tab()

    def close_tab(self):
        home, *_ = self.driver.window_handles
        self.driver.close()
        self.driver.switch_to.window(home)

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
            except (NoSuchElementException, TimeoutException) as e:
                last_page = True

    def enumerate_reports(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchResults"]/table/*')))
        results_table = self.driver.find_element(By.XPATH, '//*[@id="searchResults"]/table')
        tbodies = results_table.find_elements(By.TAG_NAME, "tbody")
        for tbody in tbodies:
            self.save_report(tbody)

    def save_report(self, tbody):
        title_row, sitting_date_row = tbody.find_elements(By.TAG_NAME, "tr")
        title_link = title_row.find_element(By.TAG_NAME, "a")
        date_em, *_ = sitting_date_row.find_elements(By.TAG_NAME, "em")
        title_text = title_link.text
        sitting_date_text = date_em.text[14:-1] # example: Sitting Date: 24-1-1968,

        if self.db.record_exists(sitting_date_text, title_text):
            with open("warnings.log", "a", encoding="utf-8") as f:
                f.write(f"{sitting_date_text} {title_text} visited before!\n")
            return

        self.driver.execute_script("arguments[0].scrollIntoView();", title_link)
        sleep(1)
        title_link.click()
        sleep(0.5)
        *_, search_results, report = self.driver.window_handles
        self.driver.switch_to.window(report)

        match = re.search(r"reportid=.*", self.driver.current_url)
        id = match.group()[9:]
        path = f"{self.path}\\{id}.json"

        try:
            section = ''
            rows = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table tr')))
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 2:
                    info_type, info = cells
                    if info_type.text.lower() == "section name:":
                        section = info.text

            content = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="showTopic"]/div')))
            # remove noise text
            self.driver.execute_script("""
                document.querySelector("table[border='1']")?.remove();
                document.querySelector(".hansardcustom table")?.remove();
                document.querySelectorAll("b,strong").forEach((element) => {
                    if (element.innerText.startsWith("Column: ")) {
                        element.remove();
                    }                
                });
                document.querySelectorAll("p[align='left']").forEach((element) => {
                    if (element.innerText.startsWith("Column: ")) {
                        element.remove();
                    }
                });
            """)
            text = content.text
            lines = [re.sub(r"^1[0-2]|0?[1-9].[0-5]?[0-9] ?[ap].m.$", "", line.strip(), flags=re.IGNORECASE) for line in text.splitlines() if line.strip()]
            lines = [re.sub(r"Column: \d+", "", line, flags=re.IGNORECASE) for line in lines]
            lines = [re.sub(r"\[.*speaker.*in the chair.*\]", "", line, flags=re.IGNORECASE) for line in lines]
            lines = [re.sub(r"^.*:", lambda m: f"#{m.group()}#", line, flags=re.IGNORECASE) for line in lines]
            text = " ".join(lines)
            speaker_loc = [speaker.span() for speaker in re.finditer("#(.*?)#", text)]
            if (len(speaker_loc) == 0):
                with open(f"{path}", "w", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "id": id,
                        "section": section,
                        "title": unidecode(title_text.strip()),
                        "date": sitting_date_text,
                        "speeches": [{
                            "name": '', 
                            "speech": unidecode(text.strip())
                        }],
                    }))
                self.db.save_record(sitting_date_text, title_text, self.driver.current_url, path)
            else:
                speaker_starts, speaker_ends = list(zip(*speaker_loc))
                speech_text_starts = speaker_ends[:]
                speech_text_ends = speaker_starts[1:] + (-1,)
                speeches_loc = list(zip(speaker_starts, speaker_ends, speech_text_starts, speech_text_ends))
                speeches = {
                    "id": id,
                    "section": section,
                    "title": unidecode(title_text.strip()),
                    "date": sitting_date_text,
                    "speeches": [
                    {
                        "name": unidecode(text[name_start+1:name_end-1]), 
                        "speech": unidecode(text[speech_text_start:(speech_text_end if speech_text_end != -1 else None)].strip())
                    } for (name_start, name_end, speech_text_start, speech_text_end) in speeches_loc
                ]}
                with open(f"{path}", "w", encoding="utf-8") as f:
                    f.write(json.dumps(speeches))
                self.db.save_record(sitting_date_text, title_text, self.driver.current_url, path)
        except Exception as e:
            with open("errors.log", "a", encoding="utf-8") as f:
                f.write(f"{self.driver.current_url} {path}: {str(e)}\n")

        self.driver.close()
        self.driver.switch_to.window(search_results)
    
    def scroll_to_bot(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

def scroll_to_bot(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

def click_at(element):
    actions = ActionChains()
    actions.move_to_element(element).click()
    actions.perform()

def main():
    parliament_number = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:")
        for opt, arg in opts:
            if opt == '-p':
                parliament_number = arg
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        quit()

    assert parliament_number != None, "Argument -p is required!"

    driver = webdriver.Chrome(service=Service("chromedriver.exe"))
    driver.get("https://sprs.parl.gov.sg/search/home")

    scroll_to_bot(driver)
    search_reports = driver.find_element(By.ID, "divmpscreen2")
    by_parliament = search_reports.find_element(By.XPATH, "//select[1]") # the first "select"
    by_parliament_select = Select(by_parliament)
    
    buttons = search_reports.find_elements(By.TAG_NAME, "button")
    assert len(buttons) == 2
    search_btn = buttons[1]
    assert search_btn.get_attribute("label") == "Search"

    advance_search_section = driver.find_element(By.ID, "accordion")
    advance_search_link = advance_search_section.find_element(By.ID, "advSearchLabel")

    # select sections
    advance_search_link.click()
    scroll_to_bot(driver)
    advance_search = Select(advance_search_section.find_elements(By.TAG_NAME, "select")[1])
    to_be_ignored = ['administration of oaths', 'all sections', 'attendance', 'permission to members to be absent']
    for index, option in enumerate(advance_search.options):
        if (option.text.lower() not in to_be_ignored):
            advance_search.select_by_index(index)

    by_parliament_select.select_by_index(parliament_number)
        
    # start searching
    search_btn.click()
    path = f"parliament\\{parliament_number}"
    if os.path.exists(path) is False:
        os.makedirs(path)
    parliament = Parliament(path, driver)
    parliament.extract_data()
    
if __name__ == "__main__":
    main()