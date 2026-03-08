#!/bin/bash

# Der Brauer Install Script for Raspberry Pi

set -e

# Check if running on Raspberry Pi
if ! grep -q "^Model\s*:\s*Raspberry Pi" /proc/cpuinfo; then
    echo "Error: This script is intended for Raspberry Pi only."
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo $0)"
    exit 1
fi

# Update system
apt update
apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv git python3-rpi.gpio python3-smbus i2c-tools

# Add user to groups
usermod -a -G gpio,i2c,dialout pi

# Enable interfaces non-interactively
raspi-config nonint do_i2c 0
raspi-config nonint do_spi 0

# Set variables
APPDIR=$(pwd)
VENVDIR="$APPDIR/venv"

# Create virtual environment
python3 -m venv "$VENVDIR"
source "$VENVDIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Customize and install service
SERVICE_FILE="/etc/systemd/system/der-brauer.service"
cp scripts/der-brauer.service "$SERVICE_FILE"
sed -i "s|{APPDIR}|$APPDIR|g" "$SERVICE_FILE"
sed -i "s|{VENVDIR}|$VENVDIR|g" "$SERVICE_FILE"

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable der-brauer
systemctl start der-brauer

# Create default .env if not exists
if [ ! -f .env ]; then
    cat << EOF > .env
DATABASE_URL=sqlite:///der_brauer.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
LOG_FILE=logs/der_brauer.log
EOF
fi

echo "Installation complete. Der Brauer service is now running."
echo "Access the dashboard at http://$(hostname -I | awk '{print $1}'):8000"