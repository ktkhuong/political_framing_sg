from time import sleep
from turtle import down
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
import re
import json
import os
import getopt
import sys
import pandas as pd

STRAITS_TIMES = 'st'
CNA = 'cna'
DOWNLOAD_DIR = "C:\\Users\\ktkhu\\Downloads"

def newest_file(dir):
    files = [f"{dir}\\{x}" for x in os.listdir(dir) if x.lower().endswith('zip')]
    newest = max(files , key = os.path.getctime)
    return newest

def count_files(dir):
    return len([f for f in os.listdir(dir) if f.lower().endswith("zip")])

class file_has_been_downloaded(object):
    def __init__(self, dir, number):
        self.dir = dir
        self.number = number

    def __call__(self, driver):
        return count_files(self.dir) > self.number

class filters_added(object):
    def __init__(self, number):
        self.number = number

    def __call__(self, driver):
        return len(driver.find_elements(By.CSS_SELECTOR, "ul[class='filters-used '] li")) > self.number

def open_link_in_tab(driver, link):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.click(link)
    actions.perform()

def sign_in(driver: webdriver.Chrome, username, password):
    WebDriverWait(driver, 30).until(EC.title_is("SSO (Login)"))
    usr = driver.find_element(By.ID, "IDToken1")
    pwd = driver.find_element(By.ID, "IDToken2")
    btn = driver.find_element(By.NAME, "Login.Submit")
    
    usr.send_keys(username)
    pwd.send_keys(password)
    btn.click()

def main():
    ys = None
    ye = None
    start = 1
    length = 500
    publication_name = STRAITS_TIMES
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:e:n:l:p:")
        for opt, arg in opts:
            if opt == '-s':
                ys = arg
            elif opt == '-e':
                ye = arg
            elif opt == '-n':
                start = int(arg)
            elif opt == '-l':
                length = int(arg)
            elif opt == '-p':
                publication_name = arg
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        quit()

    username = os.getenv("EXETER_USERNAME")
    password = os.getenv("EXETER_PASSWORD")
    assert username != None, "EXETER_USERNAME is not set as an environment variable!"
    assert password != None, "EXETER_PASSWORD is not set as an environment variable!"

    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=C:\\Users\\ktkhu\\Desktop\\Exeter\\ECMM451\\src\\data-collection\\profile')
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
    driver.get("https://advance.lexis.com/BisNexisNewsSearch")
    driver.find_element(By.CSS_SELECTOR, "a[id='idpSignIn']").click()
    try:
        btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='signInIDPBtn']")))
        btn.click()
        sign_in(driver, username, password)
        search = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[id='searchTerms']")))
        search.send_keys("Singapore")
        driver.find_element(By.CSS_SELECTOR, "button[id='mainSearch']").click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "results-list-delivery-toolbar")))
        driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource']").click()
        if publication_name == STRAITS_TIMES:
            driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource'] + ul li").click() 
        else:
            driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource'] + ul button").click()
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id='podfiltersbuttonsource'] + ul li[class='overflow']")))
            driver.find_elements(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource'] + ul li")[6].click() 
        
        WebDriverWait(driver, 30).until(filters_added(len(driver.find_elements(By.CSS_SELECTOR, "ul[class='filters-used '] li"))))
        timeline = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id='podfiltersbuttonsearch'] ~ button")))
        timeline.click()
        year_start, year_end = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "button[id='podfiltersbuttonsearch'] ~ button + div input")))
        for i in range(10):
            year_start.send_keys(Keys.BACK_SPACE)
        year_start.send_keys(ys)
        for i in range(10):
            year_end.send_keys(Keys.BACK_SPACE)
        year_end.send_keys(ye)
        driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsearch'] ~ button + div button[class='save btn secondary']").click()
        sleep(5)
        nav_last_page = driver.find_elements(By.CSS_SELECTOR, "nav[class='pagination newdesign'] li")[-2]
        driver.execute_script("arguments[0].scrollIntoView();", nav_last_page)
        nav_last_page.click()
        sleep(3)
        num_of_hits = driver.find_elements(By.CSS_SELECTOR, "ol[class='bisnexis-result-list'] li span[class='noappealwrapper']")[-1].text[:-1]
        num_of_hits = int(num_of_hits)

        for i in range(start, num_of_hits, length):
            download_btn = driver.find_element(By.XPATH, "//*[@id='results-list-delivery-toolbar']/div/ul[1]/li[4]/ul/li[3]/button")
            driver.execute_script("arguments[0].scrollIntoView();", download_btn)
            download_btn.click()
            sleep(2)
            input = driver.find_element(By.CSS_SELECTOR, "input[id='SelectedRange']")
            de = num_of_hits if (i+length-1) > num_of_hits else (i+length-1)
            input.send_keys(f"{i}-{de}")
            sleep(0.5)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            WebDriverWait(driver, 60*5).until(file_has_been_downloaded(DOWNLOAD_DIR, count_files(DOWNLOAD_DIR)))
            newest = newest_file(DOWNLOAD_DIR)
            os.rename(newest, f"{DOWNLOAD_DIR}\\{ys.replace('/','-')} {ye.replace('/','-')} {i}-{de}.zip")
            with open("nexis.log", "a") as f:
                f.write(f"Finish: {ys} {ye} {i}-{de}\n")
        sleep(30)

    except TimeoutException as e:
        print("Cannot log in!")
        quit()

    driver.close()

if __name__ == "__main__":
    main()
