# 🛠️ Power Supply Equipment

## ✅ Selected Components

### ⚡ DC 24V to 12V 30A 360W Step Down Converter

- **Model**: Waterproof Buck Power Supply Regulator (24V to 12V 30A)  
- **Price**: $20.99  
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B0CZPD94QG)

#### Specifications
- **Input**: 24V DC  
- **Output**: 12V DC @ 30A (up to 360W)  
- **Form Factor**: Waterproof, inline fuse included

#### Remarks

> ✅ *Compatible with 24–27V battery output from Scout 2.0 robot*  
> ✅ *Provides stable 12V rail for downstream devices*  
> ✅ *360W capacity ensures thermal and power headroom within 300W robot power* budget  
> ✅ *Matches Livox Mid-360 LiDAR input requirement (9–27V DC)*  
> ✅ *Supports 12V-powered external HDDs (12V 5A)  

---

### ⚡ DC 12V to 19V 10A 190W Boost Converter

- **Model**: Waterproof Power Module for Vehicle/Embedded Use  
- **Price**: $20.99  
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B0B74CXHW6)

#### Specifications
- **Input**: 12V DC  
- **Output**: 19V DC @ 10A (190W)  

#### Remarks

> ✅ *Matches Jetson AGX Orin 64GB’s recommended input (19V 10A)*  
> ✅ *Powered from 12V rail via step-down converter*

---

### 🔌 DC Barrel Plug Power Cables

#### For External HDD (12V 5A)
- **Model**: DC 2.1mm x 5.5mm Male Plug to Bare Wire (16AWG)  
- **Price**: $6.99
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B07VW5VRX7)

#### Remarks

> ✅ *Connects 12V rail to external hard disk*  
> ✅ *Rated for 5A, suitable for short-distance delivery*

#### For Jetson AGX Orin (19V 10A)
- **Model**: DC 2.5mm x 5.5mm Male Plug to Bare Wire (16AWG)  
- **Price**: $13.49  
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B0CYBXK4ZW)

#### Remarks

> ✅ *Connects 19V boost converter output to Jetson Orin*  
> ✅ *Rated for up to 10A safely over short length*

---

### 📌 Selection Rationale

This power configuration was designed for the Scout 2.0 robot to reliably power compute and sensor modules under real-world field conditions. Key considerations include:

- Stable operation within the robot’s 300W 24V supply limit
- Modular step-down and boost conversion stages for voltage isolation
- Voltage alignment with all major components (Jetson, HDD, LiDAR)
- Cable selection ensures safe current delivery under maximum load
- Waterproof converters for environmental robustness
- Scalable design for future peripheral expansion

---

### 🔧 System Power Summary

| **Component**                 | **Voltage** | **Current** | **Purpose**                | **Output Connection**                                          |
|-------------------------------|-------------|-------------|----------------------------|----------------------------------------------------------------|
| 24V → 12V Buck Converter      | 12V         | 30A max     | Primary 12V power rail     | → [12V Bus] → External HDD + Boost Converter                   |
| Livox Mid-360 LiDAR           | 12V         | ~2A         | 360° 3D LiDAR sensor       | via **direct line** from 12V Bus                               |
| External HDD (optional)       | 12V         | 5A          | External data storage      | via **16AWG**, DC **2.1mm x 5.5mm** barrel cable               |
| 12V → 19V Boost Converter     | 19V         | 10A         | Jetson Orin AGX            | → [19V Bus] → Jetson Orin AGX                                  |
| Jetson AGX Orin 64GB          | 19V         | 10A         | Jetson Orin AGX Power      | via **16AWG**, DC **2.5mm x 5.5mm** barrel cable               |

> 📌 *Designed to operate within a 300W budget, with redundant capacity and proper current-rated cables for safe and stable operation.*
