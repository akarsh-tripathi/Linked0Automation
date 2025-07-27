#!/bin/bash

# entrypoint.sh - Launch script inside container

echo "Starting LinkedIn Auto Connect Bot..."

# Set up virtual display for headless Chrome
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait for display to be ready
sleep 2

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Start the main application
echo "Launching main.py..."
python3 main.py

chmod +x entrypoint.sh
