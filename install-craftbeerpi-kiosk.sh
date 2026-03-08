#!/bin/bash
#
# CraftBeerPi Installation with Kiosk Mode for Raspberry Pi
#
# Run as sudo: sudo ./install-craftbeerpi-kiosk.sh

set -e

clear
cat << "EOF"

----------------------------------------------------------------------------

   Welcome to CraftBeerPi Installation with Kiosk Mode

     _____            __ _   ____                 _____ _____ 	  _.._..,_,_
    / ____|          / _| | |  _  \              |  __  \_  _|   (          )
   | |     _ __ __ _| |_| |_| |_) | ___  ___ _ __| |__) /| |      ]~,"-.-~~[
   | |    | '__/ _` |  _| __|  _ < / _ \/ _ \ '__|____/ | |    .=])' (;  ([
   | |____| | | (_| | | | |_| |_) |  __/  __/ |  | |    _| |_   | ]:: '    [
    \_____|_|  \__,_|_|  \__|____/ \___|\___|_|  |_|   |_____|  '=]): .)  ([
                                  (C) 2015 www.CraftBeerPI.com    |:: '    |
                                                                   ~~----~~
----------------------------------------------------------------------------

This script will install CraftBeerPi and set up the Raspberry Pi to run in kiosk mode.

EOF

# Update and upgrade system
echo "Updating and upgrading system..."
apt-get update -y
apt-get upgrade -y

# Install required packages for CraftBeerPi
echo "Installing dependencies..."
apt-get install -y python-setuptools python-dev libpcre3-dev python-smbus git

# Install pip
easy_install pip

# Clone CraftBeerPi repo
echo "Cloning CraftBeerPi repository..."
git clone https://github.com/craftbeerpi/craftbeerpi.git /opt/craftbeerpi
cd /opt/craftbeerpi

# Install Python dependencies
pip install -r requirements.txt

# Install wiringPi if needed
echo "Installing wiringPi..."
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
./build
cd ..
rm -rf WiringPi

# Setup 1-wire support
if ! grep -q "dtoverlay=w1-gpio" "/boot/config.txt"; then
    echo "Adding 1-wire support to /boot/config.txt"
    echo '# CraftBeerPi 1-wire support' >> /boot/config.txt
    echo 'dtoverlay=w1-gpio,gpiopin=4,pullup=on' >> /boot/config.txt
fi

# Install Gembird USB support (sispmctl)
apt-get install -y sispmctl

# Setup auto-start for CraftBeerPi
echo "Setting up auto-start for CraftBeerPi..."
cat > /etc/systemd/system/craftbeerpi.service <<EOL
[Unit]
Description=CraftBeerPi Server
After=multi-user.target

[Service]
User=pi
WorkingDirectory=/opt/craftbeerpi
ExecStart=/usr/bin/python /opt/craftbeerpi/runserver.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl enable craftbeerpi.service

# Now setup Kiosk Mode
echo "Setting up Kiosk Mode..."

# Install required packages for kiosk
apt-get install -y --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox chromium-browser unclutter

# Configure autologin to console
raspi-config nonint do_boot_behaviour B2

# Create .bash_profile for autologin user (assuming pi)
cat > /home/pi/.bash_profile <<EOL
[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && startx -- -nocursor
EOL

# Configure Xinitrc
cat > /home/pi/.xinitrc <<EOL
#!/bin/sh
xset -dpms
xset s off
xset s noblank

openbox-session &

while true; do
    timeout 3 bash -c "</dev/tcp/127.0.0.1/5000" >/dev/null 2>&1 && break
    sleep 1
done

exec chromium-browser --noerrdialogs --disable-session-crashed-bubble --disable-infobars --kiosk http://localhost:5000 --incognito
EOL

# Install unclutter to hide cursor
echo "unclutter -idle 0.1 -root" >> /etc/xdg/openbox/autostart

# Disable screensaver
cat >> /etc/xdg/openbox/autostart <<EOL
xset s off
xset -dpms
xset s noblank
EOL

echo "Installation complete. Rebooting to apply changes."
reboot