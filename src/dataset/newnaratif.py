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

pbar = None

def cbk(block_num, block_size, total_size):  
    '''''Callback function 
    @a:Downloaded data block 
    @b:Block size 
    @c:Size of the remote file 
    '''  
    global pbar
    if pbar is None:
        pbar = tqdm(total=100)
    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.n = 100.0*downloaded/total_size
        pbar.refresh()
    else:
        pbar.close()
        pbar = None

def open_link_in_tab(driver, link):
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.click(link)
    actions.perform()

def main():
    from_page = ''
    to_page = ''
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

    driver = webdriver.Chrome(service=Service("chromedriver.exe"))

    db = Database('newnaratif.db', 'newnaratif')
    if os.path.exists("newnaratlif") is False:
        os.makedirs("newnaratlif")

    base_url = "https://newnaratif.com"
    for i in range(from_page, to_page+1):
        url = f"{base_url}/page/{i}/?s=Singapore"
        driver.get(url)

        articles = driver.find_element(By.ID, "main").find_elements(By.TAG_NAME, "article")
        for article in articles:
            link = article.find_element(By.CSS_SELECTOR, 'h2 > a')
            driver.execute_script("arguments[0].scrollIntoView();", link)
            title = link.text
            url = link.get_attribute("href")
            open_link_in_tab(driver, link)
            sleep(1)

            *_, article_window = driver.window_handles
            driver.switch_to.window(article_window)
            sleep(1)
            url = driver.current_url
            match = re.search(r".com/.*/$", url)
            filename = match.group()[5:-1]

            try:
                date = driver.find_element(By.CSS_SELECTOR, "time[class='entry-date published']")
                main = driver.find_element(By.ID, "main")
                category = main.find_element(By.TAG_NAME, "header").find_element(By.TAG_NAME, "a")
                if category.text.lower() == "podcast":
                    iframes = main.find_elements(By.TAG_NAME, "iframe")
                    iframe = iframes[-1]
                    driver.execute_script("arguments[0].scrollIntoView();", iframe)
                    driver.switch_to.frame(iframe)
                    sleep(1)
                    audio = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'audio')))
                    match = re.search(r"/https.*cloudfront.*mp3$", audio.get_attribute("src"))
                    audio_link = unquote(match.group())[1:]
                    driver.switch_to.default_content()
                    urlretrieve(audio_link, f"newnaratlif\\{filename}.mp3", cbk)
                    db.save_record(date.text, title, url, f"newnaratlif\\{filename}.mp3")
                else:
                    driver.execute_script("""
                        document.querySelectorAll("blockquote").forEach((element) => {
                            element.remove();
                        });
                        document.querySelector("div[class='entry-byline']")?.remove();
                    """)
                    data = main.find_element(By.CSS_SELECTOR, "div[class='entry-content']")
                    with open(f"newnaratlif\\{filename}.txt", "w") as f:
                        f.write(json.dumps({
                            'title': title,
                            'date': date.text,
                            'content': data.text,
                        }))
                    db.save_record(date.text, title, url, f"newnaratlif\\{filename}.json")

                home, *_ = driver.window_handles
                driver.close()
                driver.switch_to.window(home)
            except (StaleElementReferenceException, NoSuchElementException, IndexError, AttributeError) as e:
                """ with open("errors.log", "a", encoding='utf-8') as f:
                    f.write(f"Error: {url} {str(e)}") """
                print(str(e))
                home, *_ = driver.window_handles
                driver.close()
                driver.switch_to.window(home)
    
    driver.close()

if __name__ == "__main__":
    main()