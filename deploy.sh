#!/bin/bash
# Deploy script - copies all necessary files to Raspberry Pi

set -e

# Prompt for credentials
read -p "Enter Pi username (default: pi): " PI_USER
PI_USER=${PI_USER:-pi}

read -p "Enter Pi hostname or IP (default: 192.168.88.10): " PI_IP
PI_IP=${PI_IP:-192.168.88.10}

read -sp "Enter Pi password: " PI_PASSWORD
echo ""

if [ -z "$PI_PASSWORD" ]; then
    echo "Error: Password cannot be empty"
    exit 1
fi

PI_HOST="${PI_USER}@${PI_IP}"
PROJECT_DIR="/home/${PI_USER}/bus-timings"

echo "=========================================="
echo "  Deploy Bus Timings to Raspberry Pi"
echo "  Target: $PI_HOST"
echo "=========================================="
echo ""

# Function to run commands on Pi
run_on_pi() {
    sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no "$PI_HOST" "$@"
}

echo "[1/9] Setting hostname to ch1ru..."
run_on_pi "sudo hostnamectl set-hostname ch1ru"
run_on_pi "sudo sed -i 's/127.0.1.1.*/127.0.1.1\tch1ru/' /etc/hosts"
echo "  ✓ Hostname set to ch1ru"

echo "[2/9] Creating project directory on Pi..."
run_on_pi "mkdir -p $PROJECT_DIR/src $PROJECT_DIR/config"

echo "[3/9] Copying application files..."
sshpass -p "$PI_PASSWORD" rsync -avz --progress \
    --include='src/' \
    --include='src/*.py' \
    --include='config/' \
    --include='config/*.json' \
    --include='requirements.txt' \
    --include='start.sh' \
    --include='.env.sample' \
    --exclude='*' \
    . "$PI_HOST:$PROJECT_DIR/"

echo "[4/9] Making start script executable..."
run_on_pi "chmod +x $PROJECT_DIR/start.sh"

echo "[5/9] Creating .env file if it doesn't exist..."
run_on_pi "if [ ! -f $PROJECT_DIR/.env ]; then cp $PROJECT_DIR/.env.sample $PROJECT_DIR/.env; fi"

echo "[6/9] Setting up Python virtual environment..."
run_on_pi "cd $PROJECT_DIR && python3 -m venv venv"

echo "[7/9] Installing Python dependencies..."
run_on_pi "cd $PROJECT_DIR && venv/bin/pip install --quiet --upgrade pip"
run_on_pi "cd $PROJECT_DIR && venv/bin/pip install --quiet -r requirements.txt"
echo "  ✓ Dependencies installed"

echo "[8/9] Cleaning up old services..."
run_on_pi "sudo systemctl stop bus-timings.service 2>/dev/null || true"
run_on_pi "sudo systemctl disable bus-timings.service 2>/dev/null || true"
run_on_pi "sudo rm -f /etc/systemd/system/bus-timings.service"
run_on_pi "sudo systemctl daemon-reload"

echo "[9/9] Installing bus-timings service..."
cat > /tmp/bus-timings.service << EOF
[Unit]
Description=Bus Timings Display Service
After=graphical.target network-online.target
Wants=graphical.target network-online.target

[Service]
Type=simple
User=${PI_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/start.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

sshpass -p "$PI_PASSWORD" scp /tmp/bus-timings.service "$PI_HOST:/tmp/"
run_on_pi "sudo mv /tmp/bus-timings.service /etc/systemd/system/"
run_on_pi "sudo chmod 644 /etc/systemd/system/bus-timings.service"
run_on_pi "sudo systemctl daemon-reload"
run_on_pi "sudo systemctl enable bus-timings.service"

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "To start the service:"
echo "  sudo systemctl start bus-timings.service"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u bus-timings.service -f"
echo ""
echo "To check status:"
echo "  sudo systemctl status bus-timings.service"
echo ""
