#!/bin/bash

set -e

# --- Color codes ---
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

USER_NAME=$(whoami)
PYTHON_SCRIPT="/home/$USER_NAME/AgriChrono/6_network/send_ip_email.py"
SERVICE_FILE="/etc/systemd/system/sendip.service"

echo -e "${GREEN}==== Systemd Service Creator for send_ip_email.py ====${RESET}"

# Check if python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Python script not found at $PYTHON_SCRIPT${RESET}"
    exit 1
fi

# Create systemd service file
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}Systemd service file already exists. Overwriting...${RESET}"
    sudo rm "$SERVICE_FILE"
fi

echo -e "${GREEN}Creating systemd service file...${RESET}"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Send Jetson IP via Email at boot
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 $PYTHON_SCRIPT
Restart=on-failure
User=$USER_NAME
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
echo -e "${GREEN}Reloading systemd daemon...${RESET}"
sudo systemctl daemon-reload

echo -e "${GREEN}Enabling NetworkManager-wait-online.service...${RESET}"
sudo systemctl enable NetworkManager-wait-online.service

echo -e "${GREEN}Enabling sendip.service...${RESET}"
sudo systemctl enable sendip.service

# Immediately start for test
echo -e "${GREEN}Starting sendip.service for test...${RESET}"
sudo systemctl start sendip.service

echo -e "${GREEN}==== Systemd Service Created and Started Successfully ====${RESET}"
