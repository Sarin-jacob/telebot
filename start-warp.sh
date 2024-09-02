#!/bin/sh

# Start warp-svc in the background
warp-svc &

# Wait until warp-svc is ready
until warp-cli --accept-tos status | grep -q "Status update: Connected"; do
  echo "Waiting for warp-svc to start..."
  sleep 2
done

# Connect to WARP
warp-cli --accept-tos connect

echo "WARP is connected."
