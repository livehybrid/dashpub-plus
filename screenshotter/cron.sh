#!/bin/sh

env > /etc/environment

# Function to stop gracefully
stop() {
  echo "SIGTERM caught, shutting down gracefully..."
  exit 0
}

# Set up signal handlers
trap stop TERM INT

echo "Starting screenshotter service..."

# Run the screenshotter immediately
/usr/local/bin/node /app/index.js

# Then run it every 15 minutes
while true; do
  sleep 900  # 15 minutes = 900 seconds
  /usr/local/bin/node /app/index.js
done
