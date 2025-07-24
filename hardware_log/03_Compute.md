# 💻 Compute System

## ✅ Selected Components

### 🧠 Edge Compute Unit

- **Model**: NVIDIA Jetson AGX Orin 64GB Developer Kit  
- **Price**: $1,999  
- **Purchase**: [Amazon](https://www.amazon.com/NVIDIA-Jetson-Orin-64GB-Developer/dp/B0BYGB3WV4)  
- **Status**: ✅ *Already owned*

#### Specifications
- **GPU**: Ampere architecture, 2048 CUDA cores, 64 Tensor Cores  
- **CPU**: 12-core ARM Cortex-A78AE v8.2 64-bit  
- **Memory**: 64GB LPDDR5 @ 204.8 GB/s bandwidth  
- **Storage Interface**: 1x M.2 Key M (PCIe Gen4 x4)  
- **AI Performance**: Up to **275 TOPS**  
- **Connectivity**: Includes compatible ports for **ZED Duo Link capture card**  

#### Remarks
> ✅ *ZED Link card can be directly connected and reliably stream at the desired resolution and FPS without bottlenecks*  
> ✅ *Ample compute headroom for LiDAR synchronization and real-time processing*

---

### 💾 Internal Storage

- **Model**: Samsung 990 EVO Plus SSD 4TB NVMe SSD
- **Price**: $259.99  
- **Purchase**: [Amazon](https://www.amazon.com/B0DHLBDSP7)  

#### Specifications
- **Interface**: PCIe Gen4 x4 / Gen5 x2  
- **Form Factor**: M.2 2280  
- **Sequential Read**: Up to 7,250 MB/s  

#### Remarks
> ✅ *Supports multi-stream SVO2 logging without frame drops*  
> ✅ *4TB capacity supports multiple days of dual ZED + LiDAR field recordings*

---

### 💾 External Storage (Optional)

- **Model**: WD 8TB 3.5" HDD (exact model unknown)
- **Price**: Unknown
- **Purchase**: Unknown 
- **Status**: ✅ *Already owned*

#### Specifications
- **Capacity**: 8TB  
- **Power Requirement**: Requires external 12V DC power supply

#### Remarks
> ✅ *Used as optional local backup when network/cloud sync is unavailable*  
> ✅ *Not required if data is transferred post-session over 5G or Wi-Fi*

---

### 📌 Selection Rationale

This compute configuration is designed for long-duration, remote multi-modal data collection in outdoor field environments. It provides the necessary performance to handle high-bandwidth sensor streams including dual ZED X RGB-D cameras and Livox 360° LiDAR, with on-device processing and optional backup.

- Jetson AGX Orin 64GB offers ample compute and memory headroom for real-time multi-sensor recording and processing
- Samsung 990 EVO Plus 4TB SSD offers high-speed, high-capacity local storage with sufficient margin for extended multi-camera + LiDAR sessions
- Optional 8TB HDD provides redundancy for environments with unstable network
- Designed specifically to support ZED Duo Link CSI integration and LiDAR frame alignment without performance bottlenecks
- All components are field-proven, compact, and optimized for rugged deployment with thermal efficiency and expandability

> Designed to meet the bandwidth, durability, and flexibility demands of real-world multi-sensor data logging in outdoor field settings.