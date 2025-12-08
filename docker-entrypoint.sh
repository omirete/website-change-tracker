#!/bin/bash

# Exit on error
set -e

echo "Starting website change tracker..."
echo "Script will run every half hour"

# Function to run the tracker
run_tracker() {
    echo "=================================="
    echo "Running at: $(date)"
    echo "=================================="
    python -m website_change_tracker.alert_if_missing_text
    echo "Completed at: $(date)"
    echo ""
}

# Run immediately on startup
run_tracker

# Then run every half hour (1800 seconds)
while true; do
    sleep 1800
    run_tracker
done
