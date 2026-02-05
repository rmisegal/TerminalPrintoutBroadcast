#!/bin/bash
# tunnel-keeper.sh - Keeps the tunnel alive with auto-reconnect

SHARE_DIR="/mnt/c/terminal_share"
URL_FILE="$SHARE_DIR/student_url.txt"
TUNNEL_LOG="/tmp/tunnel.log"
TUNNEL_PID="/tmp/tunnel.pid"

start_tunnel() {
    # Kill any existing tunnel
    pkill -f "ssh.*localhost.run" 2>/dev/null
    sleep 1

    # Start new tunnel
    ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:8080 nokey@localhost.run > "$TUNNEL_LOG" 2>&1 &
    echo $! > "$TUNNEL_PID"

    # Wait for URL
    for i in {1..15}; do
        sleep 1
        URL=$(grep -o 'https://[a-z0-9]*\.lhr\.life' "$TUNNEL_LOG" | head -1)
        if [ -n "$URL" ]; then
            echo "$URL" > "$URL_FILE"
            echo "[$(date '+%H:%M:%S')] Tunnel connected: $URL"
            return 0
        fi
    done
    echo "[$(date '+%H:%M:%S')] Failed to get URL"
    return 1
}

echo "Tunnel keeper started. Press Ctrl+C to stop."
echo ""

# Initial connection
start_tunnel

# Monitor and reconnect loop
while true; do
    sleep 10

    # Check if tunnel process is still running
    if [ -f "$TUNNEL_PID" ]; then
        if ! kill -0 $(cat "$TUNNEL_PID") 2>/dev/null; then
            echo "[$(date '+%H:%M:%S')] Tunnel died. Reconnecting..."
            start_tunnel
        fi
    else
        echo "[$(date '+%H:%M:%S')] Tunnel PID missing. Reconnecting..."
        start_tunnel
    fi
done
