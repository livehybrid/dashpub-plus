env > /etc/environment
echo "*/15 * * * * /usr/local/bin/node /app/index.js" | crontab -

# Make sure we react to these signals by running stop() when see them - for clean shutdown
# And then exiting
trap "stop cron; exit 0;" TERM INT

stop()
{
  # We're here because we've seen SIGTERM, likely via a Docker stop command or similar
  # Let's shutdown cleanly
  echo "SIGTERM caught, terminating cron process..."
  # Record PIDs
  pid=$(pidof cron)
  # Kill them
  kill -TERM $pid > /dev/null 2>&1
  sleep 1
  echo "Terminated."
  exit 0
}
cron -f
