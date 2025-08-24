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
