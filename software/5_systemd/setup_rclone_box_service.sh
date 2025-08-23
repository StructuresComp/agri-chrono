#!/bin/bash
set -e

# ==== Configuration ====
SERVICE_NAME="rclone-box"
REMOTE_NAME=" " # Remote name
LOCAL_MOUNT="/home/$USER/AgriChrono/box"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
RCLONE_CONFIG_DIR="/home/$USER/.config/rclone"
RCLONE_CONFIG_FILE="$RCLONE_CONFIG_DIR/rclone.conf"
CACHE_DIR="/home/$USER/.cache/rclone"

# ==== Ensure rclone is installed ====
if ! command -v rclone &> /dev/null; then
    echo "📦 Installing rclone..."
    curl https://rclone.org/install.sh | sudo bash
else
    echo "✅ rclone already installed: $(rclone version | head -n 1)"
fi

# ==== Create rclone config file ====
echo "⚙️  Writing rclone config to: $RCLONE_CONFIG_FILE"
mkdir -p "$RCLONE_CONFIG_DIR"
cat > "$RCLONE_CONFIG_FILE" <<EOF
[ ] # Remote name
type = box
token = {"access_token":" ","token_type":" ","refresh_token":" ","expiry":" ","expires_in": }
EOF
chmod 600 "$RCLONE_CONFIG_FILE"

# ==== Make sure mount path exists ====
echo "📁 Creating mount directory: $LOCAL_MOUNT"
sudo mkdir -p "$LOCAL_MOUNT"
sudo chown $USER:$USER "$LOCAL_MOUNT"

# ==== Write systemd service file ====
echo "⚙️  Writing systemd service file: $SERVICE_PATH"

sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Rclone mount for Box (System Service)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Environment=RCLONE_CONFIG=$RCLONE_CONFIG_FILE
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/rclone mount ${REMOTE_NAME} ${LOCAL_MOUNT} \\
    --vfs-cache-mode full \\
    --vfs-write-back 1s \\
    --vfs-cache-max-age 1h \\
    --cache-dir ${CACHE_DIR} \\
    --allow-other \\
    --umask 002
ExecStop=/bin/fusermount -u ${LOCAL_MOUNT}
Restart=always
User=${USER}
Group=${USER}

[Install]
WantedBy=multi-user.target
EOF

# ==== Enable FUSE allow-other ====
if ! grep -q "^user_allow_other" /etc/fuse.conf; then
    echo "🔧 Enabling 'user_allow_other' in /etc/fuse.conf"
    echo "user_allow_other" | sudo tee -a /etc/fuse.conf
fi

# ==== Enable and start service ====
echo "🚀 Enabling and starting rclone system service..."
sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo -e "\n✅ System-wide Rclone service '${SERVICE_NAME}' installed and running!"
echo "   Mount point: $LOCAL_MOUNT"
echo "   You can check status via: sudo systemctl status $SERVICE_NAME"

