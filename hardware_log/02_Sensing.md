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
- **Interface**: 22-pin CSI connection to Jetson AGX Orin (0.5mm pitch)
- **Max Resolution**: 4K @ 30 FPS per input  
- **Bandwidth**: 10 Gb/s total  
> ✅ *Enables dual ZED X input to Jetson Orin AGX via a single high-speed CSI connection*  
> ✅ *Powered directly through CSI—no separate power supply required*  
> ✅ *Supports shutter sync and external trigger for time-aligned stereo capture*

---

### 🔌 Extension Cables

- **Model**: GMSL2 Fakra Extension Cable (M-F, 0.5m)
- **Price**: $15 per unit x 2 = **$30**
- **Purchase**: [Stereolabs](https://www.stereolabs.com/store/products/gmsl2-fakra-cables)

#### Specifications
- **Compatibility**: All ZED X and ZED Link GMSL2-based systems  
> ✅ *Extends distance between ZED X cameras and Jetson Orin AGX for more flexible mounting*  

---

### 🎥 Auxiliary Streaming Camera

- **Model**: OBSBOT Tiny 2 Lite 4K Webcam  
- **Price**: $159  
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0CZ6XY78Y/)  
- **Status**: ✅ *Already owned*

#### Specifications
- **Sensor**: 1/2" CMOS  
- **Resolution**: 4K @ 30 FPS, 1080p @ 60 FPS  
- **Features**: AI tracking, PTZ (Pan-Tilt-Zoom), gesture control, built-in dual microphones, HDR  
- **Interface**: USB-C (UVC-compliant, plug-and-play)

> ✅ *Used for real-time video streaming during field operations*  
> ✅ *Selected because ZED SDK supports only one open thread, making simultaneous RGB-D recording and live video infeasible*  

---

### 📌 Selection Rationale

This stereo camera system was designed to meet the demands of real-time, long-range depth sensing in outdoor autonomous navigation. The following factors drove the selection:

- **High-accuracy depth sensing**: The ZED X 4mm offers **<0.4% error at 2m** and stable performance up to **35m**, ensuring reliable perception in large-scale field environments.
- **Optimized for outdoor navigation**: Precise depth is essential for interpreting crop rows, avoiding obstacles, and maintaining lane alignment over long distances.
- **Wide and accurate FoV**: Two cameras mounted at a **130° outward angle** achieve a combined **~150° horizontal field of view**, covering a wide scene while retaining mid-range accuracy.
- **Compact integration**: The Duo capture card connects both cameras to **Jetson AGX Orin** via a single CSI interface, with **hardware sync and no external power required**.
- **Flexible mounting**: **0.5m GMSL2 extension cables** were purchased to allow spacing between cameras and compute, enabling adjustable stereo baselines.
- **Remote monitoring capability**: Since the ZED SDK supports only one active thread, it cannot simultaneously handle RGB-D recording and live streaming.  
  To address this, an **OBSBOT Tiny 2 Lite 4K webcam** was added for **real-time video transmission** during data collection, allowing **remote observation** without interfering with high-fidelity logging.
- **Deployment readiness**: All essential components—including stereo cameras, capture card, and webcam—are **already owned**, requiring only minimal additions (cables) for full integration.

> Considering depth precision, wide coverage, real-time streaming needs, and modularity, this configuration was selected as the most practical and robust solution for RGB-D data collection in 3D reconstruction and navigation.

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
- Not suitable for **outdoor agricultural settings**, where the robot must perform **navigation tasks that require high-accuracy depth sensing even at long range**

**Decision**: Rejected due to lack of long-range accuracy and unavailability. The 4mm variant was preferred for its superior **depth precision** and **readiness for immediate deployment**.
