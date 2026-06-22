#!/bin/bash
# Start script for bus-timings application
# Sets up environment, installs dependencies, and runs the app

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
VENV_DIR="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

echo "=========================================="
echo "  Bus Timings - Starting Application"
echo "=========================================="
echo ""

# Step 1: Force HDMI display on (workaround for EDID issue)
echo "[1/2] Forcing HDMI display connection..."
echo "on" | sudo tee /sys/class/drm/card0-HDMI-A-1/status > /dev/null 2>&1 || true
sudo vcgencmd display_power 1
echo "  ✓ HDMI display enabled"

# Step 2: Run the application
echo "[2/2] Starting bus timings display..."
echo ""

export DISPLAY=:0
export SDL_VIDEODRIVER=x11

exec "$VENV_DIR/bin/python" src/main.py
