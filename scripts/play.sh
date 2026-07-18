#!/usr/bin/env bash
# Build, start, and advertise Text Dungeon on the local network.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8000}"

docker compose up -d --build

echo "Waiting for the server to come up..."
for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

PORT="$PORT" ./scripts/lan-url.sh

trap 'echo; echo "Stopping..."; docker compose down' EXIT

echo "Streaming logs -- press Ctrl+C to stop the game."
docker compose logs -f
