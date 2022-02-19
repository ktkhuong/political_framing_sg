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

    if os.path.exists("theindependent") is False:
        os.makedirs("theindependent")

    assert os.path.exists("theindependent_urls.txt"), "theindependent_urls.txt NOT found!"
    assert start != None, "Argument -s is required!"
    assert end != None, "Argument -e is required!"

    driver = webdriver.Chrome(service=Service("chromedriver.exe"))
    db = Database('theindependent.db', 'theindependent')

    if os.path.exists("theindependent") is False:
        os.makedirs("theindependent")

    with open("theindependent_urls.txt", "r") as f:
        txt = f.read()
        urls = [line.strip() for line in txt.splitlines() if line.strip()]

    for url in urls[start:end]:
        if db.record_exists(url):
            with open("errors.log", "a", encoding="utf-8") as f:
                f.write(f"{url} visited before!\n")
            continue

        driver.get(url)

        try:
            driver.execute_script("""
                document.querySelectorAll("figure,iframe,img").forEach((element) => {
                    element.remove();
                });
                document.querySelectorAll("div[class*='td-a-ad']").forEach((element) => {
                    element.remove();
                });
                document.querySelector("ul[class='sxc-follow-buttons']")?.remove();
                document.querySelector("p[class='p5'] + p")?.remove();
                document.querySelector("p[class='p5']")?.remove();
                document.querySelector("font[size='2']")?.remove();                
            """)
            title = driver.find_element(By.CSS_SELECTOR, "h2[class='tdb-title-text']")
            date = driver.find_element(By.CSS_SELECTOR, "time[class='entry-date updated td-module-date']")
            data = driver.find_element(By.XPATH, "//div[contains(@class, 'tdb_single_content')]")
            text = re.sub("Follow us on Social Media", "", data.text.strip(), flags=re.IGNORECASE)
            text = text.replace("\n", " ")
            text = text[:text.find("/TISG")]
            filename = unquote(driver.current_url[26:-1])
            path = f"theindependent\\{filename}.json"
            with open(path, "w", encoding='utf-8') as f:
                f.write(json.dumps({
                    'title': unidecode(unquote(title.text)),
                    'date': date.text,
                    'content': unidecode(unquote(text)),
                }))
                db.save_record(date.text, title.text, driver.current_url, path)
        except (StaleElementReferenceException, NoSuchElementException, IndexError) as e:
            with open("errors.log", "a", encoding='utf-8') as f:
                f.write(f"Error: {url} {str(e)}")

    driver.close()
    
if __name__ == "__main__":
    main()