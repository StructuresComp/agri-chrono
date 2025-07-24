# 🎥 Stereo Camera System

## ✅ Selected Components

### 📷 ZED X 4mm Stereo Camera (x2)

- **Model**: ZED X Stereo Camera (Lens Focal Length 4mm)
- **Price**: $599 per unit × 2 = **$1,198**
- **Purchase**: [Stereolabs](https://www.stereolabs.com/store/products/zed-x-stereo-camera)
- **Status**: ✅ *Already owned (2 units)*

#### Specifications
- **Focal Length**: 4.0 mm  
- **Field of View (FoV)**: ~80° (H) × 52° (V) × 91° (D)  
- **Aperture**: f/1.8  
- **Depth Range**: 1.0m to 35m  
- **Ideal Range**: 1.0m to 20m  
- **Depth Accuracy**:  
  - <0.4% at 2m  
  - <7% at 20m  

#### Remarks
> ✅ *High precision depth sensing over long distances*  
> ✅ *Polarizer option available for outdoor robustness*

---

### 🎛️ Stereo Camera Interface

- **Model**: ZED Link Capture Card (Duo configuration)  
- **Price**: $379  
- **Purchase**: [Stereolabs](https://www.stereolabs.com/store/products/zed-link-capture-card)  
- **Status**: ✅ *Already owned*

#### Specifications
- Supports up to **4x GMSL2 inputs** (sufficient for 2x ZED X stereo cameras)
- **Connection**: 22-pin CSI connection to Jetson AGX Orin (0.5mm pitch)
- **Max Resolution**: 4K @ 30 FPS per input  
- **Bandwidth**: 10 Gb/s total  

#### Remarks
> ✅ *Dual-camera CSI input to Jetson via single board*  
> ✅ *No external power needed (powered via CSI)*  
> ✅ *Supports hardware sync and external trigger*  

---

### 🔌 Extension Cables

- **Model**: GMSL2 Fakra Extension Cable (M-F, 0.5m)
- **Price**: $15 per unit x 2 = **$30**
- **Purchase**: [Stereolabs](https://www.stereolabs.com/store/products/gmsl2-fakra-cables)

#### Specifications
- **Compatibility**: ZED X, ZED Link Duo

#### Remarks
> ✅ *Extends distance between ZED X cameras and Jetson Orin AGX for more flexible mounting*  

---

### 🌀 3D LiDAR Sensor

- **Model**: Livox Mid-360  
- **Price**: $979  
- **Purchase**: [Livox Official](https://www.livoxtech.com/mid-360)  
- **Status**: ✅ *Already owned*

#### Specifications
- **FOV**: 360° (horizontal), -7° ~ 52° (vertical)  
- **Range**: 
  - 40 m @ 10% reflectivity
  - 70 m @ 80% reflectivity
- **Close Proximity Blind Zone²**: 0.1m
- **Point Rate**: 200,000 points/s (first return)
- **Frame Rate**: 10 Hz (typical)
- **Interface**: 100 BASE-TX Ethernet
- **Operating Temperature**: -4°F to 131°F
- **Power**: 9 ~ 27 V DC

#### Remarks
> ✅ *Designed for reliable data acquisition during long-term outdoor operation*

---

### 🎥 Auxiliary Streaming Camera

- **Model**: OBSBOT Tail Air – NDI 4K Streaming Camera  
- **Price**: $499  
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0CJLJHS3T/)  
- **Status**: ✅ *Already owned*

#### Specifications
- **Sensor**: 1/2.8” CMOS, f/1.8  
- **Resolution**: 4K @ 30 FPS, 1080p @ 60 FPS  
- **Features**: AI tracking, PTZ (Pan-Tilt-Zoom), HDR, gesture control  
- **Interface**: HDMI, USB-C, Wireless (Wi-Fi)  

#### Remarks
> ✅ *Used for real-time video streaming during field operations*  
> ✅ *3-axis gimbal with PTZ ensures stable framing and flexible view control*  
> ✅ *Selected because ZED SDK supports only one open thread, making simultaneous RGB-D recording and live video infeasible*  

---

### 📌 Selection Rationale

This sensor system is optimized for long-term, multi-modal crop data collection in real outdoor field environments. It combines wide FoV stereo vision, dense LiDAR scanning, and intuitive remote monitoring.

- Dual ZED X (4mm) cameras provide high-precision RGB-D capture with a combined 150° FoV, enabling wide-area crop coverage
- ZED Link Duo + GMSL2 extension cables enable synchronized stereo integration with flexible mounting
- Livox Mid-360 delivers 360° LiDAR coverage with stable, outdoor-ready performance
- OBSBOT Tail Air 4K offers low-latency streaming with a 3-axis gimbal and AI PTZ, allowing user-controlled remote monitoring
- All components are already owned, modular, and field-proven for continuous deployment

> Designed for robust, scalable RGB-D + LiDAR capture and remote visualization across long-term agricultural field studies.
---

## ❌ Alternatives Considered

### 📌 Option: ZED X (2.2mm Focal Length)

**Device**: [ZED X Stereo Camera – Standard Model (2.2mm)](https://www.stereolabs.com/zed-x)

**Pros**:
- Wider horizontal field of view (up to **110° H**)
- Shorter minimum depth range (starts at **0.3m**)
- Optimized for **indoor** or **close-range** applications

**Cons**:
- **Lower depth accuracy** at long range compared to the 4mm model  
- **Not available in current inventory**  
- Not suitable for **outdoor agricultural settings** requiring **long-range, high-precision depth sensing** for consistent data collection

**Decision**: Rejected due to lack of long-range accuracy and unavailability. The 4mm variant was preferred for its superior **depth precision** and **readiness for immediate deployment**.
