
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from parliament import Parliament
import re
import json
import os

def scroll_to_bot(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

def click_at(element):
    actions = ActionChains()
    actions.move_to_element(element).click()
    actions.perform()

def main():
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

    for i in range(1,len(by_parliament_select.options)):
        # select parliament
        by_parliament_select.select_by_index(i)
    # start searching
    search_btn.click()
    def on_done():
        home, *_ = driver.window_handles
        driver.switch_to.window(home)
    if os.path.exists("parliament") is False:
        os.makedirs(f"parliament")
    parliament = Parliament(f"parliament", driver)
    parliament.extract_data(on_done)
    
if __name__ == "__main__":
    main()

