# Website Change Tracker

Minimal Python script to watch a web page for changes.

## How it works
1. Gets `url_to_track` from `config.json`.
2. Fetches the page and parses the HTML contents.
3. Compares the current body to the latest snapshot stored in `states/`.
4. If differences are found, it saves a new timestamped `.html` and writes a log entry.
5. If enabled, it sends a Telegram notification upon detecting a change.

## Setup
1. Clone the repo.
2. Edit `config.json` to set the URL you want to track.
  ```JSON
  {
    "url_to_track": "your.site.to.track"
  }
  ```

3. If you want telegram notifications, create an `.env` file with:
  ```ini
  API_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
  MY_USER_ID=YOUR_TELEGRAM_USER_ID
  ```
4. Run:
  ```
  python check_status.py
  ```

## License
MIT