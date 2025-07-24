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
> ✅ *Compatible with 24V battery output from Scout 2.0 robot*  
> ✅ *High headroom (360W) ensures safe operation under 300W robot power budget*

---

### ⚡ DC 12V to 19V 10A 190W Boost Converter

- **Model**: Waterproof Power Module for Vehicle/Embedded Use  
- **Price**: $20.99  
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B0B74CXHW6)

#### Specifications
- **Input**: 12V DC  
- **Output**: 19V DC @ 10A (190W)  
- **Use Case**: Drives Jetson AGX Orin or equivalent high-power embedded systems  
> ✅ *Matches Jetson AGX Orin’s recommended input (19V 10A)*  
> ✅ *Can be fed by 12V from primary 360W step-down converter*

---

### 🔌 DC Barrel Plug Power Cables

#### For External HDD (12V 5A)
- **Model**: DC 2.1mm x 5.5mm Male Plug to Bare Wire (16AWG)  
- **Price**: $6.99
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B07VW5VRX7)  
> ✅ *Used to deliver 12V 5A power to external hard disk from the 12V rail*

#### For Jetson AGX Orin (19V 10A)
- **Model**: DC 2.5mm x 5.5mm Male Plug to Bare Wire (16AWG)  
- **Price**: $13.49  
- **Purchase**: [Amazon](https://www.amazon.com/gp/product/B0CYBXK4ZW)  
> ✅ *Used to deliver 19V 10A from boost converter to Jetson AGX Orin*

---

### 📌 Selection Rationale

This power system was designed to support multiple high-demand components on the **Scout 2.0 robot**, ensuring stable voltage delivery under field conditions. The following considerations guided the configuration:

- **Primary Power Source**: The robot supplies **24V DC up to 300W**, serving as the base input for all converters.
- **Step-down Conversion**: A **360W-rated 24V→12V converter** provides a regulated 12V power rail for peripherals, with thermal headroom and waterproof housing for outdoor use.
- **Boost Conversion**: A dedicated **12V→19V boost converter** delivers **190W** to power **Jetson Orin AGX**, matching its exact voltage and current requirements.
- **Peripheral Load Support**: An **external HDD (12V 5A, 60W)** is powered directly from the 12V rail, avoiding interference with Jetson supply.
- **Safe Current Delivery**: **16AWG DC barrel cables** were selected for both Jetson and HDD lines to safely carry **5–10A** of current over short distances.
- **Minimal, modular design**: By separating power domains into clear stages (step-down + boost), the system supports flexible wiring and future scalability without overloading any single component.

> Considering voltage compatibility, power safety, and environmental robustness, this configuration was selected as the most reliable and modular solution for field-based embedded compute and storage systems.

---

### 🔧 System Power Summary

| **Component**              | **Voltage** | **Current** | **Purpose**               | **Output Connection**                                          |
|---------------------------|-------------|-------------|----------------------------|-----------------------------------------------------------------|
| 24V → 12V Buck Converter  | 12V         | 30A max     | Primary 12V power rail     | → [12V Bus] → External HDD + Boost Converter                   |
| External HDD Power        | 12V         | 5A          | External data storage      | via **16AWG**, DC **2.1mm x 5.5mm** barrel cable               |
| 12V → 19V Boost Converter | 19V         | 10A         | Jetson Orin AGX            | → [19V Bus] → Jetson Orin AGX                                  |
| Jetson Orin AGX           | 19V         | 10A         | Jetson Orin AGX Power      | via **16AWG**, DC **2.5mm x 5.5mm** barrel cable               |


> 📌 *Designed to operate within a 300W budget, with redundant capacity and proper current-rated cables for safe and stable operation.*
