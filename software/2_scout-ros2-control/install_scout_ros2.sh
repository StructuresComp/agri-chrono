#!/bin/bash
set -e
# --- Color codes for better terminal output ---
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"
echo -e "${GREEN}==== Scout ROS 2 Full Automated Installer ====${RESET}"

# 1. Install basic dependencies and ROS 2 repo
echo -e "${GREEN}Installing basic dependencies...${RESET}"
sudo apt update
sudo apt install -y curl gnupg2 lsb-release

# Add ROS 2 repository if not already added
if [ ! -f /usr/share/keyrings/ros-archive-keyring.gpg ]; then
    echo -e "${GREEN}Adding ROS 2 repository...${RESET}"
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | \
    gpg --dearmor | sudo tee /usr/share/keyrings/ros-archive-keyring.gpg > /dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    sudo apt update
else
    echo -e "${YELLOW}ROS 2 repository already exists. Skipping.${RESET}"
fi

# 2. Install ROS 2 Humble base + teleop package
echo -e "${GREEN}Installing ROS 2 Humble base and teleop-twist-keyboard...${RESET}"
sudo apt install -y ros-humble-ros-base ros-humble-teleop-twist-keyboard

# 3. Add ROS 2 sourcing to bashrc
if grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    echo -e "${YELLOW}ROS 2 sourcing already in .bashrc. Skipping.${RESET}"
else
    echo -e "${GREEN}Adding ROS 2 sourcing to .bashrc...${RESET}"
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
fi

# 4. Install colcon and rosdep
echo -e "${GREEN}Installing colcon and rosdep...${RESET}"
sudo apt install -y python3-colcon-common-extensions python3-rosdep

# 5. Install additional dependencies
echo -e "${GREEN}Installing libasio-dev...${RESET}"
sudo apt install -y libasio-dev

# 6. Use existing workspace from AgriChrono path
WORKSPACE=~/AgriChrono/2_scout-ros2-control/ros2_ws
echo -e "${GREEN}Using existing workspace at $WORKSPACE ...${RESET}"

# 7. Build workspace
cd $WORKSPACE
echo -e "${GREEN}Building ROS 2 workspace with colcon...${RESET}"
source /opt/ros/humble/setup.bash
colcon build

# 8. Add workspace sourcing to bashrc
if grep -q "source ~/AgriChrono/2_scout-ros2-control/ros2_ws/install/setup.bash" ~/.bashrc; then
    echo -e "${YELLOW}Workspace sourcing already in .bashrc. Skipping.${RESET}"
else
    echo -e "${GREEN}Adding workspace sourcing to .bashrc...${RESET}"
    echo "source ~/AgriChrono/2_scout-ros2-control/ros2_ws/install/setup.bash" >> ~/.bashrc
fi

# Immediately source it
echo -e "${GREEN}Sourcing workspace for current shell...${RESET}"
source ~/AgriChrono/2_scout-ros2-control/ros2_ws/install/setup.bash

# 9. Install gs_usb kernel module using jetson-gs_usb-kernel-builder
echo -e "${GREEN}Installing gs_usb kernel module for current kernel...${RESET}"
cd ~/AgriChrono/2_scout-ros2-control/
# Check if jetson-gs_usb-kernel-builder.sh exists
if [ ! -f "jetson-gs_usb-kernel-builder.sh" ]; then
    echo -e "${GREEN}Downloading jetson-gs_usb-kernel-builder.sh ...${RESET}"
    wget -q https://github.com/lucianovk/jetson-gs_usb-kernel-builder/raw/main/jetson-gs_usb-kernel-builder.sh
    chmod +x jetson-gs_usb-kernel-builder.sh
else
    echo -e "${YELLOW}jetson-gs_usb-kernel-builder.sh already exists. Skipping download.${RESET}"
fi
# Run the builder
echo -e "${GREEN}Running jetson-gs_usb-kernel-builder.sh ...${RESET}"
sudo ./jetson-gs_usb-kernel-builder.sh
# Load module after build
if lsmod | grep -q gs_usb; then
    echo -e "${YELLOW}gs_usb module already loaded.${RESET}"
else
    echo -e "${GREEN}Loading gs_usb module...${RESET}"
    sudo modprobe gs_usb
fi
# Verify module
if lsmod | grep -q gs_usb; then
    echo -e "${GREEN}gs_usb kernel module successfully installed and loaded.${RESET}"
else
    echo -e "${YELLOW}Failed to load gs_usb kernel module. Please check manually.${RESET}"
fi
echo -e "${GREEN}==== Scout ROS 2 Installation Completed Successfully ====${RESET}"