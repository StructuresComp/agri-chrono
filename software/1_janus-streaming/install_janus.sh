#!/bin/bash

set -e

# --- Color codes for better terminal output ---
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${GREEN}==== Janus Gateway Full Automated Installer ====${RESET}"

# Function for installing packages
install_packages() {
    echo -e "${GREEN}Installing packages: $*${RESET}"
    sudo apt install -y "$@"
}

# 1. Install all required system dependencies
sudo apt update
sudo apt install python3-pip

install_packages libmicrohttpd-dev libjansson-dev \
    libssl-dev libsofia-sip-ua-dev libglib2.0-dev \
    libopus-dev libogg-dev libcurl4-openssl-dev liblua5.3-dev \
    libconfig-dev libsrtp2-dev v4l-utils pkg-config libtool automake \
    meson ninja-build nvidia-l4t-gstreamer
    
# 1.5 Install Python dependencies for Flask control server
echo -e "${GREEN}Installing Python dependencies (Flask, Flask-SocketIO)...${RESET}"
python3 -m pip install --upgrade pip
python3 -m pip install flask flask_socketio

# 2. Clone and build libnice
cd ~
if [ ! -d "libnice" ]; then
    echo -e "${GREEN}Cloning libnice...${RESET}"
    git clone https://gitlab.freedesktop.org/libnice/libnice
else
    echo -e "${YELLOW}libnice directory already exists. Skipping clone.${RESET}"
fi

cd libnice

if [ ! -d "build" ]; then
    echo -e "${GREEN}Building libnice...${RESET}"
    meson --prefix=/usr build
    ninja -C build
    sudo ninja -C build install
else
    echo -e "${YELLOW}libnice build directory already exists. Skipping build.${RESET}"
fi

# 3. Clone and build Janus Gateway
cd ~
if [ ! -d "janus-gateway" ]; then
    echo -e "${GREEN}Cloning janus-gateway...${RESET}"
    git clone https://github.com/meetecho/janus-gateway.git
else
    echo -e "${YELLOW}janus-gateway directory already exists. Skipping clone.${RESET}"
fi

cd janus-gateway

echo -e "${GREEN}Running autogen.sh to prepare build...${RESET}"
sh autogen.sh

echo -e "${GREEN}Configuring build...${RESET}"
./configure --prefix=/opt/janus

echo -e "${GREEN}Building janus-gateway...${RESET}"
make -j$(nproc)
sudo make install
sudo make configs

# 4. Copy janus.js from demo folder to main html folder
echo -e "${GREEN}Copying janus.js...${RESET}"
sudo cp /opt/janus/share/janus/html/demos/janus.js /opt/janus/share/janus/html/

# 5. Copy your control.html file to Janus html folder
cd ~/AgriChrono/1_janus-streaming
if [ -f control.html ]; then
    echo -e "${GREEN}Copying control.html...${RESET}"
    sudo cp control.html /opt/janus/share/janus/html/
else
    echo -e "${RED}control.html not found in current directory!${RESET}"
    exit 1
fi

# 6. Replace rtp-sample block with obsbot configuration
CONFIG_FILE="/opt/janus/etc/janus/janus.plugin.streaming.jcfg"
BACKUP_FILE="/opt/janus/etc/janus/janus.plugin.streaming.jcfg.bak"

echo -e "${GREEN}Updating streaming plugin config...${RESET}"

# Backup the config file
sudo cp "$CONFIG_FILE" "$BACKUP_FILE"

# Remove the entire rtp-sample block
sudo sed -i '/rtp-sample:/,/}/d' "$CONFIG_FILE"

# Add obsbot block at the end
sudo bash -c "cat >> $CONFIG_FILE" <<EOF

obsbot: {
  type = "rtp"
  id = 1
  description = "OBSBot H264 Stream"
  video = true
  audio = false
  videoport = 8004
  videopt = 100
  videocodec = "h264"
  videortpmap = "H264/90000"
  videobufferkf = false
}
EOF

# 7. Move janus binary (custom compiled) to /usr/local/bin
cd ~/AgriChrono/1_janus-streaming
if [ -f janus ]; then
    echo -e "${GREEN}Moving local janus binary to /usr/local/bin...${RESET}"
    sudo cp janus /usr/local/bin/janus
    sudo chmod +x /usr/local/bin/janus
else
    echo -e "${RED}Local janus binary not found in current directory!${RESET}"
    exit 1
fi

# 8. Download additional JavaScript files for WebRTC frontend
cd /opt/janus/share/janus/html/

if [ ! -f socket.io.min.js ]; then
    echo -e "${GREEN}Downloading socket.io.min.js...${RESET}"
    sudo wget https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.min.js
else
    echo -e "${YELLOW}socket.io.min.js already exists. Skipping.${RESET}"
fi

if [ ! -f adapter.min.js ]; then
    echo -e "${GREEN}Downloading adapter.min.js...${RESET}"
    sudo wget https://cdnjs.cloudflare.com/ajax/libs/webrtc-adapter/8.2.3/adapter.min.js
else
    echo -e "${YELLOW}adapter.min.js already exists. Skipping.${RESET}"
fi

echo -e "${GREEN}==== All installation and configuration completed successfully! ====${RESET}"
