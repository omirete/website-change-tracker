import json, os, time, platform
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .helpers.telegram import sendMsg
from .helpers.homeassistant import HomeAssistant

load_dotenv()

def notify(message: str, print_logs: bool = False):
    try:
        # Telegram
        user_id = os.getenv("MY_USER_ID")
        sendMsg(
            user_id=user_id,
            text=message,
            max_retries=3,
        )
    except Exception as e:
        log(f"Notification error (Telegram): {str(e)}", print_logs)
    
    try:
        # Home Assistant
        token = os.getenv("HA_TOKEN")
        notifier_id = os.getenv("HA_NOTIFICATION_TARGET")
        base_url = os.getenv("HA_BASE_URL")
        ha = HomeAssistant(token, base_url)
        ha.send_notification(message, "Website Change Tracker", notifier_id)
    except Exception as e:
        log(f"Notification error (Home Assistant): {str(e)}", print_logs)


def log(msg: str, print_to_console: bool = False):
    timestamp = datetime.now().isoformat()
    with open("log/alert_if_missing_text.log", "a", encoding="utf-8") as logfile:
        logfile.write(f"{timestamp}: {msg}\n")

    if print_to_console:
        print(f"{timestamp}: {msg}")

def setup_selenium_driver(chromium_binary: str = None, chromedriver_path: str = None) -> webdriver.Chrome:
    """
    Configure Selenium to use the system-installed Chromium and chromedriver,
    bypassing Selenium Manager.
    """
    options: Options = Options()

    # Headless Chromium - memory-optimized settings
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-default-apps")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-logging")
    
    # Single-process mode only for Linux (Pi Zero) - crashes on Windows
    # Also add memory limits for ARM devices
    if platform.system() == "Linux":
        options.add_argument("--single-process")
        # Detect if running on ARM (Raspberry Pi)
        if platform.machine().startswith('arm') or platform.machine().startswith('aarch'):
            options.add_argument("--js-flags=--max-old-space-size=256")
    
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
    
def check_if_text_present(driver: webdriver.Chrome, url: str, search_string: str, timeout: int = 20, print_logs: bool = False) -> bool:
    """Load page and check if text is present, waiting for it to appear.
    
    Returns:
        bool: True if text is found, False otherwise
    """
    
    try:
        driver.get(url)
        
        # Wait for body to be present
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for the specific text to appear in the page
        # This uses a lambda that checks if text is in page source
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: search_string in d.page_source
            )
            # Text found!
            return True
        except TimeoutException:
            # Text not found within timeout - this is expected if string is actually missing
            return False
            
    except Exception as e:
        log(f"Attempt failed: {str(e)}", print_logs)
        raise


def main(print_logs: bool = False):
    with open("config.json", "r", encoding="utf-8") as cfg_file:
        config = json.load(cfg_file)
    
    # Telegram config
    MY_USER_ID = os.getenv("MY_USER_ID")

    URL_TO_TRACK: str = config["url_to_track"]
    STRING_TO_SEARCH: str = config["string_to_search"]
    
    driver = None

    # Check environment variables first (for Docker), then config file
    CHROMIUM_BINARY = os.getenv("CHROMIUM_BINARY") or config.get("chromium_binary")
    CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH") or config.get("chromedriver_path")
    
    if CHROMIUM_BINARY and CHROMEDRIVER_PATH:
        driver = setup_selenium_driver(CHROMIUM_BINARY, CHROMEDRIVER_PATH)
    else:
        driver = setup_selenium_driver()

    try:

        # Use Selenium to check if text is present (waits for it to appear)
        text_found = check_if_text_present(
            driver=driver,
            url=URL_TO_TRACK,
            search_string=STRING_TO_SEARCH,
            timeout=20,
            print_logs=print_logs)
        
        if not text_found:
            log("String not found!", print_logs)
            if MY_USER_ID is not None:
                notify(
                    f"The string '{STRING_TO_SEARCH}' was not found at {URL_TO_TRACK}!",
                    print_logs=print_logs
                )
        else:
            log("String found.", print_logs)
    except Exception as e:
        log(f"An error occurred: {str(e)}", print_logs)
        if MY_USER_ID is not None:
            notify(
                f"Error monitoring {URL_TO_TRACK}: {str(e)}",
                print_logs=print_logs
            )
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main(True)
