#!/bin/sh

# Start warp-svc in the background
warp-svc &

# Wait for the warp-svc socket to be available
echo "Waiting for warp-svc to start..."
sleep 5  # Initial wait time for the service to start

# Loop until warp-cli can successfully connect to warp-svc
until warp-cli --accept-tos status >/dev/null 2>&1; do
  echo "Waiting for warp-svc to become ready..."
  sleep 2
done

# Connect to WARP
warp-cli --accept-tos connect

echo "WARP is connected."

# Keep the script running so the container doesn't exit
tail -f /dev/null
