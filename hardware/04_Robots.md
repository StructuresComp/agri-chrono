# 🤖 Robot Platform

## ✅ Selected Components

### 🚜 UGV Base

- **Model**: AgileX Robotics Scout 2.0  
- **Status**: ✅ *Already owned*

#### Specifications
- **Drive Type**: Differential drive (4×4 skid-steer)  
- **Max Speed**: Up to 1.5 m/s  
- **Payload Capacity**: Up to 50 kg  
- **Control Interface**: CAN, RS232/RS422, Ethernet  
- **Power**: 24V DC battery system  
- **Operating Time**: ~2–4 hours (depending on load)  

#### Remarks
> ✅ *UGV platform controllable via CAN interface*

---

### 🧱 Frame Structure

- **Material**: 8020 Aluminum Extrusion (10 Series, 1" x 1")  
- **Accessories**: 1" Black Plastic End Caps (25 Pack, compatible)  
- **Usage**: Forms the 3-layer mounting structure and enables attachment of side panels for dust shielding  
- **Status**: ✅ *Already owned*

#### Remarks
> ✅ *Lightweight, modular, reconfigurable — supports all mounting layers and side paneling*

---

### 🧩 3-Layer Component Layout

The robot platform is vertically structured into three functional layers, mounted using 8020 aluminum frame:

#### ▪️ Bottom Layer – Power + LiDAR
- **Mounted Components**:
    - DC converters (buck & boost modules)
    - Livox Mid-360 LiDAR (mounted lowest to ensure -7° to +52° vertical FoV is unobstructed)

#### ▪️ Middle Layer – Compute + Network
- **Material**: Laser-cut acrylic board
- **Mounted Components**:
    - Jetson AGX Orin (with 3D-printed customized case)
    - Network switch / 5G modem / cable routing

#### ▪️ Top Layer – Sun Shield + Streaming + Antenna
- **Material**: Acrylic board
- **Mounted Components**:
    - [Thermo-Tec 13585 adhesive heat barrier](https://www.amazon.com/dp/B000TXU55S) (reflects radiant sunlight)
    - OBSBOT Tail Air 4K streaming camera
    - MIMO antenna

#### ▪️ Side + Front Panels
- **Material**: Acrylic board
- **Purpose**:
    - Block excessive dust ingress from side wind
    - Maintain ventilation while minimizing exposure

#### Remarks
> ✅ Acrylic used for ease of drilling and thermal insulation

---

### 🎥 ZED X Mounting System

- **Vibration Isolator**: [CAME-TV Vibration Isolator](https://www.amazon.com/dp/B09ZNWQ42Q)
- **Pan-Tilt Base**: [INNOREL ZH7 Z Flex Tilt Head](https://www.amazon.com/dp/B0D9K7PS54/)

#### Mounting Structure
ZED X stereo cameras are mounted on the vibration isolator with a Z flex tilt head stacked on top. This configuration:
- Damps high-frequency vibration from robot locomotion
- Allows manual pitch/roll adjustments for stereo baseline alignment
- Enables repeatable stereo configuration with lockable tilt angles

---

### 📌 Selection Rationale

This robot platform was physically structured to maximize sensor performance, environmental durability, and ease of deployment in outdoor farmland settings. Key considerations:

- 3-tier layout separates power, compute, and communication modules with thermal and vibration isolation
- Lowest LiDAR placement ensures full vertical FoV (-7° to +52°) for accurate ground & canopy coverage
- Acrylic mid/top plates simplify drilling and insulate heat, while allowing component flexibility
- Thermal barrier on top reflects direct sunlight and protects the compute core
- OBSBOT + antenna mounted on the highest layer for optimal line-of-sight
- Dust-shielded side panels prevent ingress without blocking airflow
- Custom stereo mount (Isolator + Z Tilt) mitigates jitter and supports flexible stereo geometry
- Entire structure built from 8020 aluminum, ensuring light weight, rigidity, and modularity
> This configuration enables robust, modular, and field-ready mounting of sensors and compute for long-term remote crop data collection in real outdoor conditions.