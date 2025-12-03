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
    
def wait_for_page_stability(driver: webdriver.Chrome, timeout: int = 10, stability_time: float = 0.5) -> None:
    """Wait until page content stops changing (DOM stabilizes)."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Wait for page to stabilize by comparing page source
    last_source = None
    stable_start = None
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_source = driver.page_source
        
        if current_source == last_source:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stability_time:
                # Page has been stable for stability_time seconds
                return
        else:
            stable_start = None
            last_source = current_source
        
        time.sleep(0.1)

def get_page_with_selenium(driver: webdriver.Chrome, url: str) -> str:
    """Load page and wait for it to stabilize."""
    driver.get(url)
    wait_for_page_stability(driver)
    return driver.page_source

def find_string(page_source: str, search_string: str, print_logs: bool = False) -> bool:
    """Check if search_string is present in the given page_source."""
    try:
        soup = BeautifulSoup(page_source, "html.parser")
        page_text = soup.get_text()
        found = search_string in page_text
        
        if print_logs:
            log(f"Searched for '{search_string}': {'found' if found else 'not found'}")
        
        return found
    except Exception as e:
        if print_logs:
            log(f"String search error: {str(e)}")
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
        page_source = get_page_with_selenium(driver, URL_TO_TRACK)
        
        # Check if string is present (uses current driver state)
        if not find_string(page_source, STRING_TO_SEARCH, print_logs):
            log("String not found!", print_logs)
            if MY_USER_ID is not None:
                sendMsg(
                    user_id=MY_USER_ID,
                    text=f"The string '{STRING_TO_SEARCH}' was not found at {URL_TO_TRACK}!",
                    max_retries=3,
                )
        else:
            log("String found.", print_logs)
    except Exception as e:
        log(f"An error occurred: {str(e)}", print_logs)
        if MY_USER_ID is not None:
            sendMsg(
                user_id=MY_USER_ID,
                text=f"Error monitoring {URL_TO_TRACK}: {str(e)}",
                max_retries=3,
            )
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main(True)
