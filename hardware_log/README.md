# 🌾 3D-Farm-Reconstruction Hardware Overview

This repository documents the full hardware stack used for **RGB-D data collection**, **3D reconstruction**, and **autonomous navigation** in real farm environments.

---

## 📁 Hardware Modules

| File | Description |
|------|-------------|
| [`01_Power.md`](./01_Power.md) | Power supply and conversion system — including DC step-down and step-up regulators |
| [`02_Sensing.md`](./02_Sensing.md) | Camera systems (ZED X stereo setup, OBSBOT), IMU, and sensor synchronization |
| [`03_Compute.md`](./03_Compute.md) | Edge compute unit setup (Jetson AGX Orin), storage configuration, and thermal considerations |
| [`04_Robots.md`](./04_Robots.md) | Base platform (AgileX Scout 2.0), frame design, passive cooling, and 3D-printed integration |
| [`05_Network.md`](./05_Network.md) | Network configuration for remote control, video streaming, and system monitoring |

---

## 📌 Project Goal

To enable **real-time, high-resolution 3D reconstruction** and **crop-aware autonomous navigation** in outdoor farm settings using a compact, modular, and fully field-deployable robot.

---

## 🧩 System Highlights

- Dual **ZED X** cameras with wide-angle stereo field-of-view
- High-performance **Jetson AGX Orin 64GB** for on-device SLAM and logging
- Modular power system using **DC converters and robust cabling**
- CAN-enabled **Scout 2.0 UGV** with rugged aluminum-framed compute mount
- Sunlight and heat mitigation using **perforated aluminum mesh + thermal shielding**
- Remote monitoring via **OBSBOT 4K camera** and Janus WebRTC streaming

---

## 🚀 Status

✅ Hardware fully integrated  
🔧 Deployment-ready (tested in Fargo field trials)  
📦 All components already owned and validated

---

## 📬 Contact

Feel free to reach out via [GitHub Issues](https://github.com/Gasso21/3D-Farm-Reconstruction/issues) for questions, suggestions, or collaboration inquiries.
