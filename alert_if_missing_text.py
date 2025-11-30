import json, os, time
from datetime import datetime
from bs4 import BeautifulSoup
from helpers.telegram import sendMsg
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

def log(msg: str, print_to_console: bool = False):
    timestamp = datetime.now().isoformat()
    with open("log", "a", encoding="utf-8") as logfile:
        logfile.write(f"{timestamp}: {msg}\n")

    if print_to_console:
        print(f"{timestamp}: {msg}")

def setup_selenium_driver(chromium_binary: str = None, chromedriver_path: str = None) -> webdriver.Chrome:
    """
    Configure Selenium to use the system-installed Chromium and chromedriver,
    bypassing Selenium Manager.
    """
    options: Options = Options()

    # Headless Chromium on a Pi
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if chromium_binary:
        options.binary_location = chromium_binary
    if chromedriver_path:
        service: Service = Service(executable_path=chromedriver_path)
    else:
        service: Service = Service()

    driver: webdriver.Chrome = webdriver.Chrome(
        service=service,
        options=options,
    )
    return driver
    
def get_page_with_selenium(driver: webdriver.Chrome, url: str) -> str:
    """Fetch page content using Selenium with headless Chromium."""
    driver.get(url)

    # Wait for body to be present and give JavaScript time to execute
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    time.sleep(3)  # Additional wait for JS execution if necessary

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
    with open("config.json", "r", encoding="utf-8") as cfg_file:
        config = json.load(cfg_file)
    
    # Telegram config
    MY_USER_ID = os.getenv("MY_USER_ID")

    URL_TO_TRACK: str = config["url_to_track"]
    STRING_TO_SEARCH: str = config["string_to_search"]
    
    driver = None

    if config.get("chromium_binary") is None or config.get("chromedriver_path") is None:
        driver = setup_selenium_driver()
    else:
        CHROMIUM_BINARY: str = config["chromium_binary"]
        CHROMEDRIVER_PATH: str = config["chromedriver_path"]
        driver = setup_selenium_driver(CHROMIUM_BINARY, CHROMEDRIVER_PATH)

    try:

        # Use Selenium to get the page content with JavaScript rendering
        resp_text = get_page_with_selenium(driver, URL_TO_TRACK)
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
