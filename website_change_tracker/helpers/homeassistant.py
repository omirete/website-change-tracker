import requests

class HomeAssistant:
    def __init__(self, token, base_url, print_logs: bool = False):
        self._token = token
        self._print_logs = print_logs
        self._base_url = base_url
    
    def log(self, message: str):
        if self._print_logs:
            print(message)


    def send_notification(self, message, title, notifier_id):
        url = f"{self._base_url}/api/services/notify/{notifier_id}"
        resp = requests.post(
            url=url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            },
            json={
                "message": message,
                "title": title,
                "data": {
                    "channel": "strong_alerts",
                    "vibration_pattern": [0, 1000]
                }
            }
        )
        self.log(resp.text)
