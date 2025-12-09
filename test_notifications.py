#!/usr/bin/env python3
"""
Test script for notification system.
Tests both Telegram and Home Assistant notifications.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the package to the path
sys.path.insert(0, os.path.dirname(__file__))

from website_change_tracker.helpers.telegram import sendMsg
from website_change_tracker.helpers.homeassistant import HomeAssistant

load_dotenv()


def test_telegram():
    """Test Telegram notification."""
    print("Testing Telegram notification...")
    user_id = os.getenv("MY_USER_ID")
    api_token = os.getenv("API_TOKEN")
    
    if not user_id or not api_token:
        print("❌ Telegram: Missing credentials (MY_USER_ID or API_TOKEN in .env)")
        return False
    
    try:
        test_message = f"🧪 Test notification from Website Change Tracker\nTimestamp: {datetime.now().isoformat()}"
        sendMsg(user_id=user_id, text=test_message, max_retries=3)
        print("✅ Telegram: Notification sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Telegram: Failed to send notification - {str(e)}")
        return False


def test_home_assistant():
    """Test Home Assistant notification."""
    print("\nTesting Home Assistant notification...")
    token = os.getenv("HA_TOKEN")
    notifier_id = os.getenv("HA_NOTIFICATION_TARGET")
    
    if not token or not notifier_id:
        print("❌ Home Assistant: Missing credentials (HA_TOKEN or HA_NOTIFICATION_TARGET in .env)")
        return False
    
    try:
        ha = HomeAssistant(token)
        test_message = f"🧪 Test notification from Website Change Tracker\nTimestamp: {datetime.now().isoformat()}"
        ha.send_notification(test_message, "Website Change Tracker Test", notifier_id)
        print("✅ Home Assistant: Notification sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Home Assistant: Failed to send notification - {str(e)}")
        return False


def main():
    print("=" * 60)
    print("Website Change Tracker - Notification Test")
    print("=" * 60)
    print()
    
    telegram_ok = test_telegram()
    ha_ok = test_home_assistant()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Telegram: {'✅ PASS' if telegram_ok else '❌ FAIL'}")
    print(f"  Home Assistant: {'✅ PASS' if ha_ok else '❌ FAIL'}")
    print("=" * 60)
    
    # Exit with error code if any test failed
    if not telegram_ok and not ha_ok:
        print("\n⚠️  All notification methods failed. Check your .env configuration.")
        sys.exit(1)
    elif not telegram_ok or not ha_ok:
        print("\n⚠️  Some notification methods failed. Check the results above.")
        sys.exit(0)
    else:
        print("\n✅ All configured notification methods are working!")
        sys.exit(0)


if __name__ == "__main__":
    main()
