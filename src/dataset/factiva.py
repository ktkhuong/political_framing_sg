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
import os 
import re

def count_files(direct):
    for root, dirs, files in os.walk(direct):
        return len(list(f for f in files if f.endswith('.rtf')))

class file_has_been_downloaded(object):
    def __init__(self, dir, number):
        self.dir = dir
        self.number = number

    def __call__(self, driver):
        return count_files(self.dir) > self.number

class is_region_filtered(object):
    def __init__(self):
        pass

    def __call__(self, driver):
        return len(driver.find_element(By.ID, "NewsFilters").find_elements(By.TAG_NAME, 'li')) == 2

class is_article_loaded(object):
    def __init__(self, text):
        self.text = text

    def __call__(self, driver):
        headline = driver.find_element(By.ID, "hldSplitterPane2").find_element(By.ID, "hd").find_element(By.CLASS_NAME, "enHeadline")
        return headline.text.strip().lower() == self.text

def sign_in(driver: webdriver.Chrome):
    username = driver.find_element(By.ID, "IDToken1")
    password = driver.find_element(By.ID, "IDToken2")
    btn = driver.find_element(By.NAME, "Login.Submit")
    
    username.send_keys("tk402")
    password.send_keys("Ukw634uY0b")
    btn.click()
    search_bar = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//input[@id="atx_proxy"]')))
    return search_bar != None

def main():
    try: 
        page = 0
        while True:
            driver = webdriver.Chrome(service=Service("chromedriver.exe"))
            driver.get("https://libguides.exeter.ac.uk/factiva")
            driver.maximize_window()

            if (driver.title == "SSO (Login)"):
                success = sign_in(driver)
                if success is False:
                    print("Cannot log in!")
                    quit()

            search_input = driver.find_element(By.XPATH, '//input[@id="atx_proxy"]')
            search_input.send_keys("Singapore")
            options = driver.find_element(By.CLASS_NAME, 'dj_omnipresent_search-options-btn')
            options.click()
            date_range = driver.find_element(By.CSS_SELECTOR, 'div[class="dj_omnipresent_search-options"]').find_element(By.ID, 'dr')
            driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", date_range, "value", "_Unspecified")

            search_btn = driver.find_element(By.CLASS_NAME, 'dj_omnipresent_search-submit')
            search_btn.click()

            view = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class='fi-two fi_toggle-view']")))
            view.click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "hldSplitterPane1")))

            sources = driver.find_element(By.ID, "DiscoveryId_sc")
            strait_times = sources.find_element(By.CSS_SELECTOR, "li[title='The Straits Times - All sources']")
            driver.execute_script("arguments[0].scrollIntoView();", strait_times)
            strait_times.click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "NewsFilters")))

            singapore = driver.find_element(By.ID, "regions").find_element(By.CSS_SELECTOR, "li[title='Singapore']")
            driver.execute_script("arguments[0].scrollIntoView();", singapore) 
            singapore.click()
            WebDriverWait(driver, 30).until(is_region_filtered())

            for i in range(page):
                driver.find_element(By.ID, "headlineFrame").find_element(By.CSS_SELECTOR, "a[class='nextItem']").click()
                sleep(10)

            headlines = driver.find_element(By.ID, "headlines").find_elements(By.TAG_NAME, 'tr')
            for headline in headlines:
                link = headline.find_element(By.CSS_SELECTOR, "a[class='enHeadline']")
                driver.execute_script("arguments[0].scrollIntoView();", link) 
                link.click()
                sleep(5)

                article = driver.find_element(By.ID, "articleFrame")
                meta_data = driver.find_elements(By.CSS_SELECTOR, "div[class='article enArticle'] > div")
                info_texts = "\n".join([meta.text for meta in meta_data])
                paragraphs = article.find_elements(By.CSS_SELECTOR, "p[class='articleParagraph enarticleParagraph']")
                texts = " ".join([paragraph.text for paragraph in paragraphs])
                texts = info_texts + "\nContent: " + texts
                filename = re.sub(r'[^A-Za-z0-9 ]+', '', link.text.strip())
                with open(f"factiva\\{filename[0:150]}.txt", "w") as f:
                    f.write(texts)

            driver.close()

    except NoSuchElementException as e:
        pass

if __name__ == "__main__":
    main()
