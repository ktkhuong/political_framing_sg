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
from urllib.parse import unquote
from urllib.request import urlretrieve
import re
import json
import os
import getopt
import sys
from tqdm import tqdm

def open_link_in_tab(driver, link):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.click(link)
    actions.perform()

def main():
    from_page = None
    to_page = None
    category = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:c:")
        for opt, arg in opts:
            if opt == '-f':
                from_page = int(arg)
            elif opt == '-t':
                to_page = int(arg)
            if opt == '-c':
                category = arg
    except getopt.GetoptError as err:
        print(err)
        quit()

    driver = webdriver.Chrome(service=Service("chromedriver.exe"))

    db = Database('tremeritus.db', 'tremeritus')
    if os.path.exists(f"tremeritus\\{category}") is False:
        os.makedirs(f"tremeritus\\{category}")

    base_url = "https://www.tremeritus.net/category"
    
    for i in range(from_page, to_page+1):
        url = f"{base_url}/{category}/page/{i}/" if i > 1 else f"{base_url}/{category}/"
        driver.get(url)
        
        try:
            btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='sc-ifAKCX ljEJIv']")))
            btn.click()
        except TimeoutException as e:
            pass

        articles = driver.find_elements(By.CSS_SELECTOR, "div[class='PostContent'] ")
        for article in articles:
            link = article.find_element(By.TAG_NAME, 'a')
            driver.execute_script("arguments[0].scrollIntoView();", link)
            url = link.get_attribute("href")
            open_link_in_tab(driver, link)
            sleep(1)

            *_, article_window = driver.window_handles
            driver.switch_to.window(article_window)
            sleep(1)

            url = driver.current_url
            filename = f"{url[8:].split('/')[-2]}.json"

            try:
                driver.execute_script("""
                    document.querySelector("ul[class='ssb_list_wrapper']")?.remove();
                    document.querySelector("div[class='art-PostMetadataFooter']")?.remove();
                """)
                meta_info = driver.find_element(By.CSS_SELECTOR, "div[class='art-PostHeaderIcons art-metadata-icons']")
                date = meta_info.text.strip().split("|")[0].strip()
                title = driver.find_element(By.CSS_SELECTOR, "h2[class='art-PostHeader'] a").text
                data = driver.find_element(By.CSS_SELECTOR, "div[class='art-content'] div[class='art-Post']").find_element(By.CSS_SELECTOR, "div[class='art-PostContent']")
                path = f"tremeritus\\{category}\\{filename}.json"
                with open(path, "w", encoding='utf-8') as f:
                    f.write(json.dumps({
                        'title': title,
                        'date': date,
                        'content': data.text,
                    }))
                    db.save_record(date, title, driver.current_url, path)
                
            except (StaleElementReferenceException, NoSuchElementException, IndexError, AttributeError) as e:
                with open("errors.log", "a", encoding='utf-8') as f:
                    f.write(f"Error: {url} {str(e)}\n")

            home, *_ = driver.window_handles
            driver.close()
            driver.switch_to.window(home)
    
    driver.close()

if __name__ == "__main__":
    main()
    #s = "https://www.tremeritus.net/2021/12/27/the-peoples-report-card-on-the-arrogant-incompetent-pap-million-dollar-government/"
    #print(s[8:].split("/")[-2])
