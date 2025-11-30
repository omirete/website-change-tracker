import json, os
from datetime import datetime
from bs4 import BeautifulSoup
from helpers.telegram import sendMsg
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

def log(msg: str, print_to_console: bool = False):
    with open("log", "a", encoding="utf-8") as logfile:
        timestamp = datetime.now().isoformat()
        logfile.write(f"{timestamp}: {msg}\n")

    if print_to_console:
        print(f"{timestamp}: {msg}")

def setup_selenium_driver() -> webdriver.Chrome:
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)

    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return driver
    
def get_page_with_selenium(driver: webdriver.Chrome, url: str) -> str:
    """Fetch page content using Selenium with headless Chrome"""
    driver.get(url)
    
    # Wait for body to be present and give JavaScript time to execute
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page_source = driver.page_source
    return page_source

def find_string(driver: webdriver.Chrome, html_content: str, search_string: str) -> bool:
    # Wait until string is present
    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), search_string)
        )
        soup = BeautifulSoup(html_content, "html.parser")
        return search_string in soup.get_text()
    except:
        return False


def main(print_logs: bool = False):
    driver = setup_selenium_driver()
    try:
        # Telegram config
        MY_USER_ID = os.getenv("MY_USER_ID")


        config = json.load(open("config.json", "r", encoding="utf-8"))
        URL_TO_TRACK = config["url_to_track"]
        STRING_TO_SEARCH = config["string_to_search"]


        # Use Selenium to get the page content with JavaScript rendering
        resp_text = get_page_with_selenium(driver, URL_TO_TRACK)
        with open("latest_response.html", "w", encoding="utf-8") as f:
            f.write(resp_text)
            if not find_string(driver, resp_text, STRING_TO_SEARCH):
                log("String not found!", print_logs)
                if MY_USER_ID is not None:
                    sendMsg(
                        user_id=MY_USER_ID,
                        text=f"The string {STRING_TO_SEARCH} was not found at {URL_TO_TRACK}!",
                        max_retries=3,
                    )
            else:
                log("String found.", print_logs)
    except Exception as e:
        log(f"An error occurred: {str(e)}", print_logs)
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main(True)
