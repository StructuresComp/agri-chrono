#!/bin/bash
set -e  # Exit immediately if any command fails

# --- Terminal color codes for readable output ---
GREEN="\033[1;32m"
RESET="\033[0m"

# --- Header ---
echo -e "${GREEN}==== Full Livox SDK2 Clean Install & Sync Recorder Build ====${RESET}"

# 0. Configure eno1 interface to communicate with Livox using /etc/network/interfaces
echo -e "${GREEN}==== Setting static IP 192.168.1.100 on eno1 using /etc/network/interfaces ====${RESET}"

sudo apt update
sudo apt install -y ifupdown

# Backup existing file (if any)
sudo cp /etc/network/interfaces /etc/network/interfaces.bak.$(date +%s) || true

# Ensure eno1 is statically configured
if ! grep -q "iface eno1 inet static" /etc/network/interfaces; then
    echo -e "${GREEN}Appending static IP config for eno1 to /etc/network/interfaces...${RESET}"
    echo "" | sudo tee -a /etc/network/interfaces > /dev/null
    cat <<EOF | sudo tee -a /etc/network/interfaces > /dev/null
auto eno1
iface eno1 inet static
  address 192.168.1.100
  netmask 255.255.255.0
EOF
else
    echo -e "${GREEN}Static config for eno1 already exists in /etc/network/interfaces${RESET}"
fi

# Apply network configuration
echo -e "${GREEN}Applying network settings (ifdown/ifup) for eno1...${RESET}"
sudo ifdown eno1 || true
sudo ifup eno1 || sudo ifconfig eno1 192.168.1.100 netmask 255.255.255.0 up
sleep 2

# 1. Install cmake if not already installed
echo -e "${GREEN}==== Installing cmake ====${RESET}"
sudo apt update
sudo apt install -y cmake

# 2. Prepare workspace directory
echo -e "${GREEN}==== Preparing Livox SDK workspace ====${RESET}"
mkdir -p ~/AgriChrono/4_livox-data-tools/
cd ~/AgriChrono/4_livox-data-tools/

# 3. Clean up any previous SDK install
sudo rm -rf /usr/local/include/livox_*.h
sudo rm -rf /usr/local/lib/liblivox_lidar_sdk_shared.so*
sudo rm -rf /usr/local/lib/cmake/LivoxLidarSdk

# 4. Clone the latest Livox SDK2
echo -e "${GREEN}==== Cloning Livox-SDK2 ====${RESET}"
rm -rf Livox-SDK2
git clone https://github.com/Livox-SDK/Livox-SDK2.git

# 5. Patch file_manager.cpp to avoid hidden file error
echo -e "${GREEN}==== Patching file_manager.cpp ====${RESET}"
FILE=~/AgriChrono/4_livox-data-tools/Livox-SDK2/sdk_core/logger_handler/file_manager.cpp
sed -i '/bool ChangeHiddenFiles(/,/^}/c\bool ChangeHiddenFiles(const std::string& dir_name) { return true; }' "$FILE"
grep "ChangeHiddenFiles" "$FILE"

# 6. Build the Livox SDK2
echo -e "${GREEN}==== Building Livox SDK2 ====${RESET}"
cd ~/AgriChrono/4_livox-data-tools/Livox-SDK2/
mkdir -p build && cd build
cmake ..
make -j$(nproc)
sudo make install

# 7. Build the sync recorder
echo -e "${GREEN}==== Building custom sync recorder ====${RESET}"
cd ~/AgriChrono/4_livox-data-tools/Livox-SDK2/
rm -rf record_lidar_sync
mkdir record_lidar_sync && cd record_lidar_sync

# 8. Create recorder_sync.cpp
cat << 'EOF' > recorder_sync.cpp
#include <iostream>
#include <fstream>
#include <csignal>
#include <chrono>
#include <thread>
#include <filesystem>
#include <vector>
#include <cstring>
#include <cstdlib>
#include "livox_lidar_api.h"
#include "livox_lidar_def.h"

namespace fs = std::filesystem;
volatile bool stop_signal = false;
bool ready_sent = false;

std::ofstream ofs_pointcloud;
std::ofstream ofs_imu;
double sync_time = 0.0;

void signal_handler(int signum) { stop_signal = true; }

double current_system_time() {
    auto now = std::chrono::system_clock::now();
    auto now_us = std::chrono::time_point_cast<std::chrono::microseconds>(now);
    return now_us.time_since_epoch().count() / 1e6;
}

void PointCloudCallback(uint32_t handle, uint8_t dev_type, LivoxLidarEthernetPacket* data, void* client_data) {
    if (!data || data->dot_num == 0) return;
    double ts_now = current_system_time();
    double rel_ts = ts_now - sync_time;

    if (!ready_sent) {
        std::cout << "[READY] Livox" << std::endl;
        ready_sent = true;
    }

    uint32_t dot_num = data->dot_num;
    ofs_pointcloud.write(reinterpret_cast<char*>(&rel_ts), sizeof(double));
    ofs_pointcloud.write(reinterpret_cast<char*>(&dot_num), sizeof(uint32_t));

    if (data->data_type == kLivoxLidarCartesianCoordinateLowData) {
        const LivoxLidarCartesianLowRawPoint* points = reinterpret_cast<const LivoxLidarCartesianLowRawPoint*>(data->data);
        for (uint32_t i = 0; i < dot_num; i++) {
            float x = points[i].x, y = points[i].y, z = points[i].z;
            float intensity = static_cast<float>(points[i].reflectivity);
            ofs_pointcloud.write(reinterpret_cast<char*>(&x), sizeof(float));
            ofs_pointcloud.write(reinterpret_cast<char*>(&y), sizeof(float));
            ofs_pointcloud.write(reinterpret_cast<char*>(&z), sizeof(float));
            ofs_pointcloud.write(reinterpret_cast<char*>(&intensity), sizeof(float));
        }
    }
}

void ImuCallback(uint32_t handle, uint8_t dev_type, LivoxLidarEthernetPacket* data, void* client_data) {
    if (!data) return;
    double ts_now = current_system_time();
    double rel_ts = ts_now - sync_time;
    float* imu = reinterpret_cast<float*>(data->data + 8);
    ofs_imu.write(reinterpret_cast<char*>(&rel_ts), sizeof(double));
    ofs_imu.write(reinterpret_cast<char*>(imu), sizeof(float) * 6);
}

void WorkModeCallback(livox_status status, uint32_t handle, LivoxLidarAsyncControlResponse* response, void*) {
    if (!response) return;
    EnableLivoxLidarPointSend(handle, nullptr, nullptr);
    EnableLivoxLidarImuData(handle, nullptr, nullptr);
}

void LidarInfoChangeCallback(uint32_t handle, const LivoxLidarInfo* info, void*) {
    if (!info) return;
    std::cout << "Lidar detected SN: " << info->sn << std::endl;
    SetLivoxLidarPclDataType(handle, kLivoxLidarCartesianCoordinateLowData, nullptr, nullptr);
    SetLivoxLidarWorkMode(handle, kLivoxLidarNormal, WorkModeCallback, nullptr);
}

double load_sync_time(const std::string& out_dir) {
    std::string file_path = out_dir + "/../sync_time.txt";
    while (!fs::exists(file_path)) {
        std::cout << "[" << file_path << "] Waiting for sync_time.txt..." << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    std::ifstream infile(file_path);
    double st;
    infile >> st;
    return st;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Usage: " << argv[0] << " <config.json> <output_dir>" << std::endl;
        return -1;
    }
    signal(SIGINT, signal_handler);

    std::string config_path = argv[1], output_dir = argv[2];
    fs::create_directories(output_dir);
    sync_time = load_sync_time(output_dir);

    LivoxLidarSdkInit(config_path.c_str());
    LivoxLidarSdkStart();

    ofs_pointcloud.open(output_dir + "/pointcloud_sync.bin", std::ios::binary);
    ofs_imu.open(output_dir + "/imu_sync.bin", std::ios::binary);

    if (!ofs_pointcloud.is_open() || !ofs_imu.is_open()) {
        std::cerr << "\u274C Failed to open output files." << std::endl;
        return -1;
    }

    SetLivoxLidarPointCloudCallBack(PointCloudCallback, nullptr);
    SetLivoxLidarImuDataCallback(ImuCallback, nullptr);
    SetLivoxLidarInfoChangeCallback(LidarInfoChangeCallback, nullptr);

    while (!stop_signal)
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

    ofs_pointcloud.close();
    ofs_imu.close();
    LivoxLidarSdkUninit();
    std::cout << "Recording stopped." << std::endl;
    return 0;
}
EOF

# 9. Write CMakeLists.txt for the custom recorder
cat << 'EOF' > CMakeLists.txt
cmake_minimum_required(VERSION 3.5)
project(livox_sdk2_sync_recorder)
set(CMAKE_CXX_STANDARD 17)
include_directories(/usr/local/include)
link_directories(/usr/local/lib)
add_executable(recorder_sync recorder_sync.cpp)
target_link_libraries(recorder_sync livox_lidar_sdk_shared pthread)
EOF

# 10. Compile the sync recorder
echo -e "${GREEN}==== Compiling recorder_sync ====${RESET}"
mkdir -p build && cd build
cmake ..
make -j$(nproc)

# 11. Completion message
echo -e "${GREEN}==== COMPLETE ====${RESET}"
echo "✅ recorder_sync ready at:"
echo "~/AgriChrono/4_livox-data-tools/Livox-SDK2/record_lidar_sync/build/recorder_sync"