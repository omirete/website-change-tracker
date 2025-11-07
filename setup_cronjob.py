"""
Create/ensure a cron job for the website change tracker.

Notes
- Works on Linux/macOS using the `crontab` CLI.
- On Windows, prints a helpful message (use Task Scheduler instead).
"""

import os
import sys
import platform
import subprocess
import shlex

# Every two hours
CRON_SCHEDULE = "0 */2 * * *"  # Every 2 hours

# Absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "detect_website_changes.py")
LOG_PATH = os.path.join(SCRIPT_DIR, "cron.log")


def _quote(path: str) -> str:
    """Quote a shell argument for POSIX shells used by cron.
    Using shlex.quote keeps spaces safe.
    """
    return shlex.quote(path)


def setup_cronjob():
    system = platform.system()
    if system == "Windows":
        print(
            "Cron is not available on Windows. Use Task Scheduler or run this on a Linux/macOS system."
        )
        return

    # Use the current Python interpreter to avoid hard-coding a path.
    python_exe = sys.executable or "/usr/bin/env python3"

    # Ensure we run in the project directory (cron's CWD is not your repo).
    cron_command = (
        f"cd {_quote(SCRIPT_DIR)} && "
        f"{_quote(python_exe)} {_quote(SCRIPT_PATH)} >> {_quote(LOG_PATH)} 2>&1"
    )
    cron_line = f"{CRON_SCHEDULE} {cron_command}\n"

    # Read existing crontab (if any). Non-zero exit means 'no crontab for user'.
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        print(
            "'crontab' command not found. Please install cron (cronie) and try again."
        )
        return

    existing = ""
    if result.returncode == 0:
        existing = result.stdout or ""

    if cron_command in existing:
        print("Cron job already exists.")
        return

    # Append new line to current crontab and load it via `crontab -`.
    new_crontab = (existing.rstrip("\n") + "\n" if existing else "") + cron_line

    try:
        subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
        print(
            "Cron job added successfully. You can check that it worked correctly by running 'crontab -l'."
        )
    except subprocess.CalledProcessError as exc:
        print("Failed to install crontab entry:")
        print(exc)
        return

    print("Cron job added successfully.")


if __name__ == "__main__":
    setup_cronjob()
