# 🔧 Hardware Overview

## 1. Platform Description

<table>
<tr>
<td width="55%" valign="top">

The robotic platform is purpose-built for **long-term deployment in outdoor farmland**.  
It is designed to withstand:  
- Prolonged sun exposure  
- Fluctuating weather  
- Uneven terrain  

During **4 weeks** of summer field trials, the system operated **4 sessions per day** in temperatures exceeding **100°F**, validating:  
- Durability  
- Thermal stability  
- Continuous sensing reliability  

This ensures stable, multi-modal data acquisition under dynamic outdoor conditions.

</td>
<td width="45%">

<img src="../assets/Figure_2.png" alt="Hardware Platform" width="100%"/>

</td>
</tr>
</table>

---

## 2. Tiered System Architecture

- **Bottom Tier – Ground Perception**  
  - **Livox Mid-360 LiDAR** mounted at the lowest point to utilize its vertical FoV ($-7^\circ$ to $+52^\circ$).  
  - Provides unobstructed crop-level scanning without occlusion from upper components.  

- **Middle Tier – RGB-D Capture**  
  - Dual **ZED X stereo cameras** mounted on vibration-isolated, tilt-adjustable heads.  
  - Outward angle of ~130°, achieving ~150° combined horizontal FoV.  
  - Isolation reduces high-frequency vibration; tilt adapts to crop growth stages.  

- **Top Tier – Situational Awareness**  
  - **OBSBOT Tail Air 4K PTZ camera** for panoramic live streaming.  
  - Remotely controlled to monitor forward, lateral, and downward directions.  

---

## 3. Communication & Compute

- **5G Router + omnidirectional antenna** for stable low-latency remote control and streaming.  
- **Jetson AGX Orin 64GB** as the onboard compute unit, handling sensor fusion and data logging.  
- **CAN-based control** of the AgileX Scout 2.0 ensures reliable navigation on uneven farmland.  
- **Dedicated DC converters** regulate voltage directly from the UGV’s main battery.  
- **Thermal shielding and custom chassis** (aluminum–acrylic) mitigate heat and provide protection.  

---

## 4. Hardware Modules

| File | Description |
|------|-------------|
| [`01_Power.md`](./01_Power.md)   | Power supply and conversion system |
| [`02_Sensing.md`](./02_Sensing.md) | Camera systems (ZED X stereo, OBSBOT), LiDAR, sensor synchronization |
| [`03_Compute.md`](./03_Compute.md) | Edge compute (Jetson AGX Orin), storage, and thermal design |
| [`04_Robots.md`](./04_Robots.md)   | Base UGV (Scout 2.0), frame design, and custom integration |
| [`05_Network.md`](./05_Network.md) | Network configuration for teleoperation, streaming, and monitoring |

---

## 5. Key Features

- Dual **ZED X stereo cameras** for wide-angle RGB-D capture with vibration-isolated mounts  
- **Livox Mid-360 LiDAR** for 360° 3D point cloud sensing  
- Remote streaming and control with **OBSBOT 4K + WebRTC**  
- High-performance **Jetson AGX Orin** for multi-sensor integration
- Sun and heat protection for stable outdoor operation

---

## **📜 Citation**  
```tex
@article{,
  title={},
  author={},
  journal={},
  year={}
}
```