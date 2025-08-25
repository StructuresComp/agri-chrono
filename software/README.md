# 💻 Software Overview

## 1. System Description

<table>
<tr>
<td width="55%" valign="top">

The software stack enables **multi-modal sensing, control, and remote operation** on Jetson AGX Orin 64GB.  
It supports:  
- Synchronized RGB-D + LiDAR + IMU logging  
- CAN-based AGV control (AgileX Scout 2.0)  
- Low-latency WebRTC streaming with browser teleoperation  
- Automated data offload and network reporting

Each module is self-contained and ships with an **`.sh` auto-installer** for one-command setup.

</td>
<td width="45%">

<img src="../assets/Figure_2.png" alt="Hardware Platform" width="100%"/>

</td>
</tr>
</table>

---

## 2. Modular Architecture

- **1_streaming — Remote Teleoperation**  
  - Janus Gateway + GStreamer for WebRTC video; Flask-SocketIO UI for PTZ, Scout teleop, system monitoring, and synchronized recording start/stop.  
  - UI overlay shows Wi-Fi/CPU/SSD/robot speed; safe key release on blur/disconnect.

- **2_scout — Robot Control (CAN + ROS 2)**  
  - Based on **AgileX** repo: [scout_ros2](https://github.com/agilexrobotics/scout_ros2)  
  - `ugv_sdk` **patched for Ubuntu 22.04 / ROS 2 Humble** (reference patch: [commit link](https://github.com/lucaslins0035/scout_ros2/commit/f0facda7757d75bc0336d700b2f5ae9f384b42f3))  
  - **gs_usb**: JetPack **6.2 (L4T 36.4.3)** lacks this module; we build it externally (kernel module) and load it during install.  
  - Workspace (`ros2_ws/src`): `scout_base`, `scout_description`, `scout_msgs` (submodules) + patched `ugv_sdk`.

- **3_zed — RGB-D Logging**  
  - Dual ZED X capture to `.svo2` (L/R) + per-frame IMU CSV, **aligned to `sync_time.txt`**.  
  - ZED dependencies (JetPack 6.2 / L4T 36.4):  
    - `stereolabs-zedlink-duo_1.3.0-LI-MAX96712-all-L$T36.4.0_arm64.deb`  
    - `ZED_SDK_Tegra_L4T36.4_v5.0.2.zstd.run`  
  - Typical settings: HD1080 @ 15 FPS, Depth=NEURAL, Compression=LOSSLESS.

- **4_livox — LiDAR Logging**  
  - Based on **Livox SDK2**: [Livox-SDK2](https://github.com/Livox-SDK/Livox-SDK2)  
  - Custom recorder (`4_livox-data-tools/Livox-SDK2/record_lidar_sync/recorder_sync.cpp`) writes:  
    - `pointcloud_sync.bin` (rel-time + N + XYZ + intensity)  
    - `imu_sync.bin` (rel-time + accel/gyro)  
  - **Aligned to `sync_time.txt`** for cross-modal synchronization.

- **5_systemd — Data Services**  
  - **Auto-transfer**: plug external HDD → udev triggers mount → `transfer.py` copies today/ yesterday folders to `/mnt/<USER>/fargo`, emails status, unmounts.  
  - **Cloud backup (Box)**: `rclone` systemd service mounts Box at `~/AgriChrono/box` with cache and `allow-other`.

- **6_network — Connectivity Services**  
  - Boot-time systemd service emails: **Jetson IPs, Wi-Fi SSID, link speed** — ideal for headless deployments and quick remote access.

---

## 3. Software Modules

| Directory | Description |
|-----------|-------------|
| `1_janus-streaming/` | WebRTC streaming + teleop UI (Janus, Flask, Socket.IO) |
| `2_scout-ros2-control/` | ROS 2 CAN control (AgileX stack, patched `ugv_sdk`, gs_usb built for L4T 36.4.3) |
| `3_zed-data-tools/` | Dual ZED X RGB-D logger (`.svo2` + IMU CSV, ZED SDK 5.0.2 / ZED Link Duo) |
| `4_livox-data-tools/` | Livox Mid-360 LiDAR + IMU logger (SDK2 + custom C++ recorder) |
| `5_systemd/` | External HDD auto-transfer + rclone Box system service |
| `6_network/` | Boot-time IP/SSID/link-speed email notifier |

---

## 4. Directory Structure (top-level)

``` swift
AgriChrono/
├── 1_janus-streaming/
│   ├── install_janus.sh
│   ├── control.html
│   └── control_server.py
├── 2_scout-ros2-control/
│   ├── install_scout_ros2.sh
│   └── ros2_ws/
│       └── src/ (scout_base, scout_description, scout_msgs, ugv_sdk)
├── 3_zed-data-tools/
│   └── data_svo_sync.py
├── 4_livox-data-tools/
│   ├── install_livox_sdk2_sync.sh
│   └── Livox-SDK2/record_lidar_sync/recorder_sync.cpp
├── 5_systemd/
│   ├── install_transfer_service.sh
│   ├── setup_rclone_box_service.sh
│   └── transfer.py
├── 6_network/
│   ├── create_sendip_service.sh
│   └── send_ip_email.py
└── data/
    └── fargo/ (site1-1, site1-2, site2, site3, ...)
```

---

## 5. Synchronized Data Layout

``` swift
/fargo/<site>/<YYYYMMDD_HHMM>/
├── sync_time.txt
├── RGB-D/
│   ├── L.svo2
│   ├── R.svo2
│   ├── L_info.csv
│   └── R_info.csv
└── LiDAR/
    ├── pointcloud_sync.bin
    └── imu_sync.bin
```

---

## 6. Safety & Ops

- **Fail-safe teleop**: browser blur/disconnect clears keys and sends zero Twist.  
- **Network watchdogs**: boot-time IP email; easy remote access without GUI.  
- **Hands-off data management**: plug-and-go HDD offload + Box cloud mount.

---

## 7. Environment & Versions

- **JetPack 6.2 (L4T 36.4.x)** on Jetson AGX Orin 64GB  
- **ROS 2 Humble**  
- **ZED**: ZED Link Duo (`stereolabs-zedlink-duo_1.3.0-LI-MAX96712-all-L$T36.4.0_arm64.deb`), **ZED SDK 5.0.2** (`ZED_SDK_Tegra_L4T36.4_v5.0.2.zstd.run`)  
- **Livox**: SDK2 (latest) + custom `recorder_sync.cpp`  
- **Kernel module**: **gs_usb** built for **L4T 36.4.3**