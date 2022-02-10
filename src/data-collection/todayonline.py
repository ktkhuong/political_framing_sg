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

    if os.path.exists("todayonline") is False:
        os.makedirs("todayonline")

    with open("todayonline\\links.txt", "r") as f:
        txt = f.read()
        urls = [line.strip() for line in txt.splitlines() if line.strip()]

    db = Database('todayonline.db', 'todayonline')

    #chrome_options = Options()
    #chrome_options.add_argument('user-data-dir=C:\\Users\\ktkhu\\Desktop\\Exeter\\ECMM451\\src\\data-collection\\profile')
    #driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
    driver = webdriver.Chrome(service=Service("chromedriver.exe"))

    for url in urls[start:end]:
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "section div[class='text']")))      
            date = driver.find_element(By.CSS_SELECTOR, "div[class='article__row article__row--']")
            title = driver.find_element(By.CSS_SELECTOR, "section h1[class='h1 h1--page-title']")
            data = driver.find_element(By.CSS_SELECTOR, "section div[class='text']")
            text = " ".join([line.strip() for line in data.text.splitlines() if line.strip()])
            url = driver.current_url
            *_, filename = url[8:].split("/")
            path = f"todayonline\\{filename}.json"
            with open(f"{path}", "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "title": title.text,
                    "date": date.text[10:],
                    "content": text
                })) 
                db.save_record(date.text, title.text, url, path)
            
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException, IndexError) as e:
            with open("errors.log", "a", encoding='utf-8') as f:
                f.write(f"Error: {driver.current_url} {str(e)}")

    driver.close()

if __name__ == "__main__":
    main()