from io import TextIOWrapper
import json, os
import unicodedata
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
from helpers.telegram import sendMsg
from dotenv import load_dotenv

load_dotenv()

def log(msg: str, print_to_console: bool = False):
    with open("log", "a", encoding="utf-8") as logfile:
        timestamp = datetime.now().isoformat()
        logfile.write(f"{timestamp}: {msg}\n")

    if print_to_console:
        print(f"{timestamp}: {msg}")

def get_last_known_state() -> TextIOWrapper:
    states = os.listdir("states")
    if len(states) > 0:
        filename = max(states)
        return read_state(filename=filename)
    else:
        return None


def read_state(filename: str) -> TextIOWrapper:
    filepath = os.path.join("states", filename)
    return open(filepath, "r", encoding="utf-8")


def save_state(state: str, filename: str = None):
    if filename is None:
        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = timestamp
    # Ensure the 'states' directory exists
    os.makedirs("states", exist_ok=True)
    with open(os.path.join("states", f"{filename}.html"), "w", encoding="utf-8") as f:
        f.write(state)


def has_changes(state_from_response: str) -> bool:

    aux_state_name = "0000-00-00T00-00-00.000000_aux_state"
    save_state(state_from_response, aux_state_name)
    current_state = read_state(f"{aux_state_name}.html").read()
    current_state = unicodedata.normalize("NFC", current_state)
    os.remove(os.path.join("states", f"{aux_state_name}.html"))

    last_known_state = get_last_known_state()
    last_known_state = "" if last_known_state is None else last_known_state.read()
    last_known_state = unicodedata.normalize("NFC", last_known_state)

    soup_a = BeautifulSoup(current_state, "html.parser")
    soup_b = BeautifulSoup(last_known_state, "html.parser")

    body_a = soup_a.body
    body_b = soup_b.body

    return body_a != body_b


def main():
    try:
        # Telegram config
        MY_USER_ID = os.getenv("MY_USER_ID")


        config = json.load(open("config.json", "r", encoding="utf-8"))
        URL_TO_TRACK = config["url_to_track"]

        resp = get(URL_TO_TRACK)
        if resp.status_code == 200:
            resp_text = resp.text
            if has_changes(resp_text):
                log("Change detected!")
                if MY_USER_ID is not None:
                    sendMsg(
                        user_id=MY_USER_ID,
                        text=f"The website at {URL_TO_TRACK} has changed!",
                        max_retries=3,
                    )
                save_state(resp_text)
            else:
                log("No changes detected.")
                pass
        else:
            log(f"HTTP Request was not successful. Status: {resp.status}")
    except Exception as e:
        log(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
