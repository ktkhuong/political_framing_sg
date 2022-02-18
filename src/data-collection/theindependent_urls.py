from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from database import Database
from unidecode import unidecode
from urllib.parse import unquote
import re
import json
import os
import getopt
import sys

def open_link_in_tab(driver, link):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.click(link)
    actions.perform()

def main():
    start = None
    end = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:e:")
        for opt, arg in opts:
            if opt == '-s':
                start = int(arg)
            elif opt == '-e':
                end = int(arg)
    except getopt.GetoptError as err:
        print(err)
        quit()

    assert start != None, "Argument -s is required!"
    assert end != None, "Argument -e is required!"

    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=C:\\Users\\ktkhu\\Desktop\\Exeter\\ECMM451\\src\\data-collection\\profile')
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)

    base_url = "https://theindependent.sg/news/singapore-news"
    close_notification = False
    for page in range(start, end+1):
        url = f"{base_url}/page/{page}"
        driver.get(url)

        # in case notification dialog pops up
        try:
            if close_notification is False:
                btn = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'onesignal-slidedown-cancel-button')))
                btn.click()
                close_notification = True
        except TimeoutException as e:
            close_notification = True

        links = driver.find_elements(By.CSS_SELECTOR, "div[class='td_block_inner tdb-block-inner td-fix-index'] > div a[class='td-image-wrap']")
        hrefs = [link.get_attribute("href") for link in links if not link.get_attribute("title").lower().startswith("stories you might")]
        with open("theindependent_urls.txt", "a") as f:
            f.write("\n".join(hrefs))
            f.write("\n")

    driver.close()

    assert os.path.exists("theindependent_urls.txt"), "theindependent_urls.txt NOT found!"
    
if __name__ == "__main__":
    main()