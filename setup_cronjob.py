#!/usr/bin/env python3
"""
Script to automatically set up a cronjob for the website change tracker.
This script will add a cron entry to run detect_website_changes.py at regular intervals.
"""

import sys

import subprocess
from pathlib import Path
import shutil


def get_current_directory():
    """Get the absolute path of the script's directory."""
    return Path(__file__).parent.resolve()



def get_poetry_path():
    """Get the absolute path to the poetry binary, or None if not found."""
    poetry_path = shutil.which("poetry")
    return poetry_path

def check_poetry_available():
    """Check if poetry is available and return its path if so."""
    poetry_path = get_poetry_path()
    if poetry_path is None:
        return None
    try:
        subprocess.run(
            [poetry_path, "--version"],
            capture_output=True,
            check=True
        )
        return poetry_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_existing_crontab():
    """Get the current user's crontab."""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True
        )
        # Return empty string if no crontab exists (exit code 1)
        return result.stdout if result.returncode == 0 else ""
    except FileNotFoundError:
        print("Error: 'crontab' command not found. This script requires cron to be installed.")
        sys.exit(1)

def get_run_interval():
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid hours value '{sys.argv[1]}'. Must be an integer.")
            sys.exit(1)
    else:
        print("How often should the script run?")
        hours_input = input("Enter number of hours (default: 1): ").strip()
        if hours_input == "":
            hours = 1
        else:
            try:
                hours = int(hours_input)
            except ValueError:
                print(f"Error: Invalid input '{hours_input}'. Must be an integer.")
                sys.exit(1)
    return hours

def get_script_name() -> str:
    """Get the script filename to run."""
    print("Which script do you want to setup a cronjob for?")
    print("1) detect_website_changes.py (default)")
    print("2) alert_if_missing_text.py")
    script_id = input("Enter 1 or 2: ").strip()
    if script_id == "":
        script_name = "detect_website_changes.py"
    else:
        if script_id == "1":
            script_name = "detect_website_changes.py"
        elif script_id == "2":
            script_name = "alert_if_missing_text.py"
        else:
            print(f"Error: Invalid input '{script_id}'. Must be 1 or 2.")
            sys.exit(1)
    return script_name


def create_cron_entry(hours: int, script_dir: Path, poetry_path: str, script_filename: str) -> str:
    """Create a cron entry string using the absolute poetry path."""
    log_path = "cron.log"
    cron_schedule = f"0 */{hours} * * *"
    # Use the absolute poetry path
    command = f"cd {script_dir} && {poetry_path} run python {script_filename} >> {log_path} 2>&1"
    return f"{cron_schedule} {command}"


def setup_cronjob(script_name: str, hours: int = 1):
    """
    Set up a cronjob to run the website change tracker.
    
    Args:
        hours: How often to run the script (in hours)
    """
    if hours < 1:
        print("Error: Hours must be at least 1")
        sys.exit(1)
    
    # Check if poetry is available and get its path
    poetry_path = check_poetry_available()
    if not poetry_path:
        print("Error: Poetry is not installed or not available in PATH.")
        print("This script requires Poetry to be installed.")
        print("Visit for installation instructions: https://python-poetry.org")
        sys.exit(1)

    script_dir = get_current_directory()

    print(f"Setting up cronjob to run every {hours} hour(s)...")
    print(f"Script directory: {script_dir}")
    print(f"Poetry binary: {poetry_path}")
    print(f"Command: {poetry_path} run python detect_website_changes.py")

    # Get existing crontab
    existing_crontab = get_existing_crontab()

    # Check if our cronjob already exists
    marker = "website-change-tracker"
    if marker in existing_crontab:
        print("\nA cronjob for website-change-tracker already exists.")
        response = input("Do you want to replace it? (y/n): ").lower().strip()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)

        # Remove existing entries
        lines = existing_crontab.split('\n')
        existing_crontab = '\n'.join([line for line in lines if marker not in line])

    # Create new cron entry with absolute poetry path
    new_entry = create_cron_entry(hours, script_dir, poetry_path, script_name)
    new_entry_with_comment = f"# {marker}\n{new_entry}"

    # Combine with existing crontab
    if existing_crontab.strip():
        updated_crontab = existing_crontab.rstrip() + '\n' + new_entry_with_comment + '\n'
    else:
        updated_crontab = new_entry_with_comment + '\n'

    # Install new crontab
    try:
        process = subprocess.Popen(
            ["crontab", "-"],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(input=updated_crontab)

        if process.returncode == 0:
            print("\n✓ Cronjob successfully installed!")
            print(f"\nThe script will run every {hours} hour(s).")
            print(f"Cron entry: {new_entry}")
            print(f"\nLogs will be written to: {script_dir / 'cron.log'}")
            print("\nTo view your crontab, run: crontab -l")
            print("To remove the cronjob, run: crontab -e")
        else:
            print("\n✗ Failed to install cronjob.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error installing cronjob: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("=== Website Change Tracker - Cronjob Setup ===\n")

    # Check if running on Windows
    if sys.platform == "win32":
        print("Warning: This script is designed for Linux/Unix systems with cron.")
        print("For Windows, consider using Task Scheduler instead.")
        response = input("Do you want to continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            sys.exit(0)
    
    # Get script name to run from user
    script_name = get_script_name()

    # Get interval from user
    hours = get_run_interval()
    
    setup_cronjob(script_name, hours)


if __name__ == "__main__":
    main()
