
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

    advance_search_section = driver.find_element(By.ID, "accordion")
    advance_search_link = advance_search_section.find_element(By.ID, "advSearchLabel")

    # select sections
    advance_search_link.click()
    scroll_to_bot(driver)

    advance_search_section.find_element(By.CSS_SELECTOR, "input[id='byMP']").click()
    current_mp = Select(advance_search_section.find_element(By.TAG_NAME, "select"))
    for option in current_mp.options:
        with open("parliament_mp.txt", "a") as f:
            f.write(option.text + "\n")

    advance_search_section.find_element(By.CSS_SELECTOR, "input[id='byFMP']").click()
    mp = Select(advance_search_section.find_element(By.TAG_NAME, "select"))
    for option in mp.options:
        with open("parliament_mp.txt", "a") as f:
            f.write(option.text + "\n")

if __name__ == "__main__":
    main()