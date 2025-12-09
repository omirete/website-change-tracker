# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for Chromium and Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml and README.md for installation
COPY pyproject.toml README.md ./
COPY website_change_tracker ./website_change_tracker
RUN pip install --no-cache-dir .

# Copy config file
COPY config.json ./

# Copy test script
COPY test_notifications.py ./

# Create directories for states and logs
RUN mkdir -p states

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
