#!/bin/bash
# Orange Pi Zero 2W LCD Monitor - Installation Script
# For Waveshare 1.44inch LCD HAT

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/opiz2w-monitor"
SERVICE_NAME="lcd-monitor"

echo "=========================================="
echo "  Orange Pi Zero 2W LCD Monitor Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Please run as root (sudo ./install.sh)"
    exit 1
fi

# Check for Orange Pi Zero 2W
echo "[1/6] Checking system..."
if ! grep -q "OrangePi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This doesn't appear to be an Orange Pi board."
    echo "         The installer will continue anyway."
fi

# Install system dependencies
echo "[2/6] Installing system dependencies..."
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-pil \
    python3-numpy \
    python3-psutil \
    fonts-dejavu-core

# Install Python packages
echo "[3/6] Installing Python packages..."
pip3 install --break-system-packages luma.lcd 2>/dev/null || pip3 install luma.lcd
pip3 install --break-system-packages OPi.GPIO 2>/dev/null || pip3 install OPi.GPIO

# Copy project files
echo "[4/6] Installing monitor application..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/drivers" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/pages" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/utils" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/monitor.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/monitor.py"

# Install systemd service
echo "[5/6] Installing systemd service..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Orange Pi LCD Monitor
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/monitor.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=${INSTALL_DIR}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo "[6/6] Installation complete!"
echo ""
echo "=========================================="
echo "  Usage:"
echo "=========================================="
echo ""
echo "  Start service:    sudo systemctl start ${SERVICE_NAME}"
echo "  Stop service:     sudo systemctl stop ${SERVICE_NAME}"
echo "  Enable on boot:   sudo systemctl enable ${SERVICE_NAME}"
echo "  View logs:        sudo journalctl -u ${SERVICE_NAME}"
echo ""
echo "  Run manually:     sudo python3 ${INSTALL_DIR}/monitor.py"
echo "  Simulation mode:  python3 ${INSTALL_DIR}/monitor.py --sim"
echo ""
echo "=========================================="
echo "  Note: SPI1 must be enabled first!"
echo "  Run: sudo ./enable_spi1.sh"
echo "=========================================="
