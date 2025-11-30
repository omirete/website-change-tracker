# Website Change Tracker

Minimal Python script to watch a web page for changes.

## How it works
1. Gets `url_to_track` from `config.json`.
2. Fetches the page and parses the HTML contents.
3. Compares the current body to the latest snapshot stored in `states/`.
4. If differences are found, it saves a new timestamped `.html` and writes a log entry.
5. If enabled, it sends a Telegram notification upon detecting a change.

## What you will need
1. Any Python version >=3.9 (and less than 4.0, I suppose). Get it from [here](https://www.python.org/downloads/).
2. [Poetry](https://python-poetry.org/docs/#installation) for managing dependencies and virtual environments.

## Setup
1. Clone the repo.
2. Create a `config.json` file in the project root to set the URL you want to track and the string you would like to search for, if you want to do that as well.
  ```JSON
  {
    "url_to_track": "your.site.to.track",
    "string_to_search": "some string"
  }
  ```
3. If you want telegram notifications, create an `.env` file with:
  ```ini
  API_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
  MY_USER_ID=YOUR_TELEGRAM_USER_ID
  ```
4. Install dependencies with Poetry:
  ```
  poetry install
  ``` 
5. Run it once to test everything works as expected:
  ```
  poetry run python detect_website_changes.py
  ```
  or with
  ```
  poetry run python alert_if_missing_text.py
  ```
6. Optionally setup a cronjob using the wizard:
  ```
  poetry run python setup_cronjob.py
  ```

## License
MIT
