
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
    def __init__(self, parliament_number: str, driver: webdriver.Chrome) -> None:
        self.parliament_number = parliament_number
        self.driver = driver

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
        title_row, *_ = tbody.find_elements(By.TAG_NAME, "tr")
        title_link = title_row.find_element(By.TAG_NAME, "a")

        self.driver.execute_script("arguments[0].scrollIntoView();", title_link)
        sleep(1)
        title_link.click()
        sleep(0.5)
        *_, search_results, report = self.driver.window_handles
        self.driver.switch_to.window(report)
        
        if not os.path.exists(".\\parliament"):
            os.makedirs(".\\parliament")

        with open(f".\\parliament\\urls_{self.parliament_number}.txt", "a") as f:
            f.write(f"{self.driver.current_url}\n")

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
    parliament = Parliament(parliament_number, driver)
    parliament.extract_data()
    
if __name__ == "__main__":
    main()