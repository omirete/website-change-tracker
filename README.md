# Website Change Tracker

Monitors a web page and alerts when specific text is missing. Runs automatically every hour in a Docker container.

## How it works
1. Reads `url_to_track` and `string_to_search` from `config.json`
2. Fetches the page using Chromium/Selenium (handles JavaScript-rendered content)
3. Searches for the specified text
4. If the text is not found, sends notifications via Telegram and/or Home Assistant
5. Logs all activity to a log file

## Setup

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/omirete/website-change-tracker.git
   cd website-change-tracker
   ```

2. Create `config.json`:
   ```json
   {
     "url_to_track": "https://example.com",
     "string_to_search": "text to monitor"
   }
   ```

3. (Optional) Set up notifications:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   - `API_TOKEN`: Telegram bot token (get from @BotFather)
   - `MY_USER_ID`: Your Telegram user ID (get from @userinfobot)
   - `HA_TOKEN` & `HA_NOTIFICATION_TARGET`: Home Assistant credentials (optional)

4. Start the container:
   ```bash
   docker-compose up -d
   ```

5. View logs:
   ```bash
   docker-compose logs -f
   ```

6. Stop the container:
   ```bash
   docker-compose down
   ```

## Testing Notifications

To verify your notification setup is working correctly:

### Method 1: Test inside the running container
```bash
docker-compose exec website-change-tracker python test_notifications.py
```

### Method 2: Run a one-off test container
```bash
docker-compose run --rm website-change-tracker python test_notifications.py
```

### Method 3: Test locally (if you have Python installed)
```bash
python test_notifications.py
```

The test script will:
- Check if your credentials are configured in `.env`
- Send test messages via Telegram and/or Home Assistant
- Display success/failure status for each notification method

**Note**: At least one notification method (Telegram or Home Assistant) should be configured for the tracker to send alerts.

## Notes
- The script runs immediately on startup, then every half hour
- The `states/` directory and `log` file persist between container restarts
- You can edit `config.json` without rebuilding the container
- Chromium and chromedriver are pre-configured

## License
MIT
