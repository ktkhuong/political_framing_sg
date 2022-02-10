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
    from_page = None
    to_page = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:")
        for opt, arg in opts:
            if opt == '-f':
                from_page = int(arg)
            elif opt == '-t':
                to_page = int(arg)
    except getopt.GetoptError as err:
        print(err)
        quit()

    assert from_page != None, "Argument -f is required!"
    assert to_page != None, "Argument -t is required!"

    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=C:\\Users\\ktkhu\\Desktop\\Exeter\\ECMM451\\src\\data-collection\\profile')

    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=chrome_options)

    db = Database('theindependent.db', 'theindependent')
    if os.path.exists("theindependent") is False:
        os.makedirs("theindependent")

    base_url = "https://theindependent.sg/news/singapore-news"
    for i in range(from_page, to_page+1):
        url = f"{base_url}/page/{i}"
        driver.get(url)

        # in case notification dialog pops up
        try:
            btn = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'onesignal-slidedown-cancel-button')))
            btn.click()
        except TimeoutException as e:
            pass

        articles = driver.find_elements(By.CSS_SELECTOR, "div[class='td_block_inner tdb-block-inner td-fix-index'] > div")
        for article in articles:
            meta_info = article.find_element(By.CLASS_NAME, "td-module-meta-info")
            link = meta_info.find_element(By.CSS_SELECTOR, 'h3 > a')
            driver.execute_script("arguments[0].scrollIntoView();", link)
            title = link.text
            url = link.get_attribute("href")
            open_link_in_tab(driver, link)
            sleep(1)

            *_, article_window = driver.window_handles
            driver.switch_to.window(article_window)

            try:           
                driver.execute_script("""
                    document.querySelectorAll("figure,iframe,img").forEach((element) => {
                        element.remove();
                    });
                    document.querySelector("ul[class='sxc-follow-buttons']")?.remove();
                    document.querySelector("p[class='p5'] + p")?.remove();
                    document.querySelector("p[class='p5']")?.remove();
                    document.querySelector("font[size='2']")?.remove();
                """)
                date = driver.find_element(By.CSS_SELECTOR, "time[class='entry-date updated td-module-date']")
                data = driver.find_element(By.XPATH, "//div[contains(@class, 'tdb_single_content')]")
                text = re.sub("Follow us on Social Media", "", data.text.strip(), flags=re.IGNORECASE)
                text = text.replace("\n", " ")
                filename = driver.current_url[26:-1]
                path = f"theindependent\\{filename}.json"
                with open(path, "w", encoding='utf-8') as f:
                    f.write(json.dumps({
                        'title': unidecode(title),
                        'date': date.text,
                        'content': unidecode(text),
                    }))
                    db.save_record(date.text, title, driver.current_url, path)
                home, *_ = driver.window_handles
                driver.close()
                driver.switch_to.window(home)
            except (StaleElementReferenceException, NoSuchElementException, IndexError) as e:
                with open("errors.log", "a", encoding='utf-8') as f:
                    f.write(f"Error: {url} {str(e)}")
            home, *_ = driver.window_handles
            driver.close()
            driver.switch_to.window(home)
    
    driver.close()

if __name__ == "__main__":
    main()