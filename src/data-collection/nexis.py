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
from selenium_stealth import stealth
from database import Database
from unidecode import unidecode
import re
import json
import os
import getopt
import sys
import pandas as pd

def count_files(direct):
    for root, dirs, files in os.walk(direct):
        return len(list(f for f in files if f.endswith('.zip')))

class file_has_been_downloaded(object):
    def __init__(self, dir, number):
        self.dir = dir
        self.number = number

    def __call__(self, driver):
        return count_files(self.dir) > self.number

def open_link_in_tab(driver, link):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.click(link)
    actions.perform()

def sign_in(driver: webdriver.Chrome):
    WebDriverWait(driver, 30).until(EC.title_is("SSO (Login)"))
    username = driver.find_element(By.ID, "IDToken1")
    password = driver.find_element(By.ID, "IDToken2")
    btn = driver.find_element(By.NAME, "Login.Submit")
    
    username.send_keys("tk402")
    password.send_keys("Ukw634uY0b")
    btn.click()

def main():
    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=C:\\Users\\ktkhu\\Desktop\\Exeter\\ECMM451\\src\\data-collection\\profile')
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)
    driver.get("https://advance.lexis.com/BisNexisNewsSearch")
    driver.find_element(By.CSS_SELECTOR, "a[id='idpSignIn']").click()
    try:
        btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='signInIDPBtn']")))
        btn.click()
        sign_in(driver)
        search = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[id='searchTerms']")))
        search.send_keys("Singapore")
        driver.find_element(By.CSS_SELECTOR, "button[id='mainSearch']").click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#results-list-delivery-toolbar > div > ul:nth-child(1) > li.expandable > ul > li.lastUsed > button")))
        driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource']").click()
        driver.find_element(By.CSS_SELECTOR, "button[id='podfiltersbuttonsource'] + ul li").click()
        sleep(5)
        for i in range(1,86467,500):
            driver.find_element(By.CSS_SELECTOR, "#results-list-delivery-toolbar > div > ul:nth-child(1) > li.expandable > ul > li.lastUsed > button").click()
            sleep(1)
            input = driver.find_element(By.CSS_SELECTOR, "input[id='SelectedRange']")
            input.send_keys(f"{i}-{i+499}")
            filename = driver.find_element(By.CSS_SELECTOR, "input[id='FileName']")
            filename.clear()
            filename.send_keys(f"{i}-{i+499}")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            WebDriverWait(driver, 60*5).until(file_has_been_downloaded("C:\\Users\\ktkhu\\Downloads", count_files("C:\\Users\\ktkhu\\Downloads")))

    except TimeoutException as e:
        print("Cannot log in!")
        quit()

    driver.close()

if __name__ == "__main__":
    main()