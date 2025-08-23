#!/bin/bash

set -e

# --- Setup ---
USER_NAME=$(whoami)
PY_SCRIPT="/home/$USER_NAME/AgriChrono/5_systemd/transfer.py"
SERVICE_FILE="/etc/systemd/system/transfer.service"
UDEV_RULE="/etc/udev/rules.d/99-transfer.rules"
MOUNT_SCRIPT="/usr/local/bin/mount_and_transfer.sh"
LOG_FILE="/home/$USER_NAME/AgriChrono/transfer_log.txt"

GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${GREEN}==== Installing Auto Transfer Service ====${RESET}"

# 1. Check Python script exists
if [ ! -f "$PY_SCRIPT" ]; then
    echo -e "${RED}Python script not found: $PY_SCRIPT${RESET}"
    exit 1
fi

# 2. Create log file
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

# 3. Create systemd service
echo -e "${GREEN}Creating systemd service: $SERVICE_FILE${RESET}"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Auto transfer data to /mnt/$USER_NAME when mounted or detected
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $PY_SCRIPT
User=$USER_NAME
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 4. Create mount_and_transfer.sh script
echo -e "${GREEN}Creating mount script: $MOUNT_SCRIPT${RESET}"
sudo bash -c "cat > $MOUNT_SCRIPT" <<EOF
#!/bin/bash

LOG_FILE="/home/$USER_NAME/AgriChrono/transfer_log.txt"
echo "[mount_and_transfer] Invoked at \$(date)" >> \$LOG_FILE

# Mount with proper permissions
if mount -o uid=$USER_NAME,gid=$USER_NAME /dev/sda1 /mnt/$USER_NAME >> \$LOG_FILE 2>&1; then
    echo "[mount_and_transfer] Mounted /dev/sda1 to /mnt/$USER_NAME successfully." >> \$LOG_FILE
else
    echo "[mount_and_transfer] Failed to mount /dev/sda1" >> \$LOG_FILE
    exit 1
fi

sleep 3

# Launch transfer only if mountpoint exists
if mountpoint -q /mnt/$USER_NAME; then
    echo "[mount_and_transfer] Starting transfer.service..." >> \$LOG_FILE
    systemctl start transfer.service
else
    echo "[mount_and_transfer] /mnt/$USER_NAME is not a mountpoint" >> \$LOG_FILE
fi
EOF

sudo chmod +x $MOUNT_SCRIPT


# 5. Create udev rule
echo -e "${GREEN}Creating udev rule: $UDEV_RULE${RESET}"
sudo bash -c "cat > $UDEV_RULE" <<EOF
KERNEL=="sda1", ACTION=="add", ENV{DEVTYPE}=="partition", RUN+="/usr/bin/systemd-run --no-block $MOUNT_SCRIPT"
EOF

# 6. Reload systemd and udev
echo -e "${GREEN}Reloading systemd and udev...${RESET}"
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo udevadm control --reload-rules

# 7. Enable service (doesn't auto-start, just for reference)
# echo -e "${GREEN}Enabling transfer.service (manual start allowed)...${RESET}"
# sudo systemctl enable transfer.service

echo -e "${GREEN}✅ Installation complete. Plug in the external disk to trigger transfer.service${RESET}"