# AgriChrono: A Multi-modal Dataset Capturing Crop Growth and Illumination Variability via a Field Robot Platform

## 1. Overview

<table>
<tr>
<td width="65%" valign="top">

- **Project Duration**: July 2–31, 2025  
- **Location**: NDSU Experimental Field  
- **Objective**: Capture time-aligned RGB-D + LiDAR data across three distinct crop sites.  
- **Focus**: **Site 1 is the primary focus**, and **Site 2 and 3 are supplementary**.  

</td>
<td width="35%">

<img src="./assets/Figure_1.png" alt="Overview Image" width="100%"/>

</td>
</tr>
</table>

---

## 2. Field Layout

<p align="center">
  <img src="./assets/Figure_3_v3.png" alt="NDSU Experimental Field" style="width:100%;"/>
</p>

**Main Field Structure**:
- `Site 1`: Regular Canola (main target crop)
- `Site 2`: Flax Trial
- `Site 3`: Canola Genotype Trial



---

## 3. Data Collection Protocol

### 📆 Collection Periods

| Phase       | Dates           | Frequency             | Purpose                                       |
|-------------|------------------|------------------------|-----------------------------------------------|
| Phase 1     | July 2–21        | 4× daily, 7 days/week | Active growth tracking & lighting variation   |
| Phase 2     | July 22–31       | 4× daily, 2 days/week | Growth slowed (near maturity), reduced need   |

---

### 🧪 Site-wise Collection Frequency

| Site   | Description                   | Sessions per Day | Days per Week  | Period           |
|--------|-------------------------------|------------------|----------------|------------------|
| Site 1 | Main Canola Site              | 4                | 7              | July 2–21        |
|        |                               | 4                | 2              | July 22–31       |
| Site 2 | Flax Trial (Side)             | 1–2 (selected)   | 2              | July 2–31        |
| Site 3 | Canola Genotype Trial (Side)  | 1–2 (selected)   | 2              | July 2–31        |

---

### 🛠 Field Conditions

- ❌ **Rainy days**: Data collection was skipped
- ✅ **Wet soil**: Wooden boards were used to allow UGV traversal without damaging soil/crops
- ☀️ **Lighting Diversity**: Sampling times:
  - 06:00 AM (sunrise)
  - 11:00 AM (late morning / high-angle sun)
  - 04:00 PM (late afternoon / descending sun)
  - 09:00 PM (sunset)

---

## 4. Site Descriptions

### 🌼 Site 1: Main Canola Site
- **Dimensions**: 50 ft (length) × 3 ft (width), 4 rows per plot with 9-inch row spacing
- **Planting Date**: June 1, 2025
- **Emergence Date**: June 7, 2025 (~6 days after sowing)
- **Variety**: *InVigor L340PC* (Spring Canola Hybrid)
- **First Flowering Date**: July 10, 2025
- **Crop Duration**: 90–110 days
- **Objective**:  
  To comprehensively record how a single canola variety appears across growth stages and varying lighting conditions.  
  *This serves as the core reference site for building a robust RGB-D dataset resilient to changes in time, illumination, and crop development.*



---

### 🌿 Site 2: Flax Trial Site
- **Design**: 4 blocks × 4 plots = 16 total plots
- **Plot Size**: 8 ft × 3 ft per plot
- **Planting Date**: May 30, 2025
- **Variety**: *Gold ND* (Open-Pollinated Flax Cultivar)
- **Crop Duration**: 90–120 days
- **Weed Control Treatments**:
  - 3 blocks sprayed with herbicide using a robot
  - 1 block hand-weeded
- **Objective**:  
  To compare structural patterns of flax under different weed control treatments in a multi-plot setting.  
  *This trial supplements the dataset with structural diversity across crop type and site layout, supporting broader training scenarios.*

---

### 🌼 Site 3: Canola Genotype Trial Site
- **Design**: 11 blocks, each measuring 44 ft × 3 ft
- **Genetic Lines**: 44 different canola genotypes per block
- **Planting Date**: May 30, 2025
- **Objective**:  
  To examine morphological variation across diverse canola genotypes using a large number of distributed plots.  
  *This enables exploration of crop-level diversity essential for robust 3D modeling and perception systems.*

---

## 5. Data Structure

### Raw data format (`raw_data/[site]/[timestamp]/`)


```swift
[timestamp]/
├── LiDAR/
│   ├── imu_sync.bin              ← Raw IMU data from Mid-360 LiDAR
│   ├── pointcloud_sync.bin       ← Timestamped LiDAR point clouds (binary)
├── RGB-D/
│   ├── L.svo2                    ← Left ZED X SVO recording
│   ├── L_info.csv                ← Left ZED IMU and timestamp info
│   ├── R.svo2                    ← Right ZED X SVO recording
│   ├── R_info.csv                ← Right ZED IMU and timestamp info
├── sync_time.txt                 ← Global time sync info (ZED ↔ LiDAR)
```

### Extracted data format (`extracted_data/[site]/`)

```swift
[site]/
├── [timestamp]_RGB.mp4           ← 4 RGB views: L_L, L_R, R_L, R_R
├── [timestamp]_Depth.mp4         ← RGB + Depth views: L_L_RGB, R_L_RGB, L_L_Depth, R_L_Depth
├── [timestamp]_Lidar.mp4         ← RGB + Depth + LiDAR point clouds
├── [timestamp].tar.gz            ← Compressed archive of the extracted [timestamp]/ folder
```

### Extracted session folder (`extracted_data/[site]/[timestamp]/`)

```swift
[timestamp]/
├── depth_npz_L/                  ← Depth (.npz) aligned to L_L
│   ├── 00000.npz
├── depth_npz_R/                  ← Depth (.npz) aligned to R_L
│   ├── 00000.npz
├── depth_png_L/                  ← Depth visualization (.png), aligned to L_L
│   ├── 00000.png
├── depth_png_R/                  ← Depth visualization (.png), aligned to R_L
│   ├── 00000.png
├── frame_L/                      ← PNG RGB frames from left ZED X
│   ├── L_00000.png               ← L_L camera
│   ├── R_00000.png               ← L_R camera
├── frame_R/                      ← PNG RGB frames from right ZED X
│   ├── L_00000.png               ← R_L camera
│   ├── R_00000.png               ← R_R camera
├── lidar/
│   ├── 00000.ply                 ← LiDAR point cloud for frame 0
│   ├── lidar_info.csv            ← Per-frame IMU + timestamp for LiDAR
├── zed_info.csv                  ← Combined IMU + timestamp info from ZED L & R
```

### CSV Format Overview

#### `zed_info.csv`

| Column                     | Description                                         |
|----------------------------|-----------------------------------------------------|
| `L_frame_id`, `R_frame_id` | Matched frame IDs from left/right ZED              |
| `L_timestamp`, `R_timestamp` | Absolute timestamps (in seconds)                 |
| `relative_time`           | Time elapsed from the first ZED frame (starts at 0.0) |
| `L_*`, `R_*`              | IMU data from each ZED (accel_x/y/z, gyro_x/y/z)    |

#### `lidar_info.csv`

| Column          | Description                                      |
|------------------|--------------------------------------------------|
| `frame_id`      | Frame index aligned with ZED relative time        |
| `timestamp`     | Relative timestamp (ZED-aligned)                  |
| `accel_*`, `gyro_*` | IMU data from LiDAR at the corresponding time |
