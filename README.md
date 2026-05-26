
<p align="center">
  <h1 align="center"><strong> AgriChrono: A Multi-modal Dataset Capturing Crop Growth and Lighting Variability with a Field Robot</strong></h1>
</p>

<p align="center">
  <a href="https://jaehwan-j.github.io">Jaehwan Jeong</a><sup>1,2</sup>, <a href="https://tuananh1007.github.io">Tuan-Anh Vu</a><sup>2</sup>, Mohammad Jony<sup>3</sup>, Shahab Ahmad<sup>3</sup>,<br>
  Md. Mukhlesur Rahman<sup>3</sup>, Sangpil Kim<sup>1,†</sup>, and M. Khalid Jawed<sup>2,†</sup><br><br>
  <sup>1</sup>Korea University, &nbsp; 
  <sup>2</sup>University of California, Los Angeles, &nbsp; 
  <sup>3</sup>North Dakota State University
</p>


<div align="center">
  <a href="https://arxiv.org/pdf/2508.18694v2">
    <img src="https://img.shields.io/badge/arXiv-2508.18694-red?logo=arxiv" alt="arXiv Badge">
  </a>
  <a href="https://jaehwan-j.github.io/projects/agrichrono/agrichrono.html">
    <img src="https://img.shields.io/badge/Project-Page-blue?logo=website" alt="Project Page">
  </a>
  <a href="https://jaehwan-j.github.io/agrichrono/">
    <img src="https://img.shields.io/badge/Benchmark-Page-orange?logo=website" alt="Benchmark Page">
  </a>
  <a href="benchmark/README.md">
    <img src="https://img.shields.io/badge/Benchmark-NVS-yellow">
  </a>
  <a href="datasets/README.md">
    <img src="https://img.shields.io/badge/Dataset-18%20TB-green">
  </a>
</div>

## 1. Project Overview
<table>
<tr>
<td width="60%" valign="top">

- **Duration**: July 2 – August 1, 2025  
- **Location**: NDSU Experimental Field, Fargo, ND
- **Objective**: Capture time-aligned RGB-D, LiDAR, IMU, and Pose data across three crop sites under realistic outdoor conditions
- **Focus Sites**: 
  - **Site 1**: Primary canola site, with repeated daily captures across growth stages and lighting variations
  - **Site 2**: Canola genotype trial with 44 varieties for morphological diversity
  - **Site 3**: Flax trial site with structural variability from differing weed control strategies

</td>
<td width="40%">
<img src="./assets/Figure_1.png" alt="Overview Image" width="100%"/>
</td>
</tr>
</table>
<table width="100%">
  <tr>
    <td width="37.8%">
      <img src="./assets/AgriChrono_Video.gif" width="100%">
    </td>
    <td width="36%">
      <img src="./assets/AgriChrono_Streaming.gif" width="100%">
    </td>
    <td width="25.6%">
       <img src="./assets/AgriChrono_Data.gif" width="100%">
    </td>
  </tr>
</table>

---

## 2. System Resources

<table>
<tr>
<td width="60%" valign="top">

🔧 [**Hardware Documentation**](hardware/README.md)  
Robot platform, sensor layout, power system, and networking design for long-term deployment  

💻 [**Software Stack**](software/README.md)  
Control interfaces, real-time streaming modules, and logging mechanisms used during collection  

📊 [**NVS Benchmark**](benchmark/README.md)  
Novel View Synthesis benchmark on AgriChrono across seven scenarios featuring lighting variance and growth span.

💾 [**AgriChrono Dataset**](datasets/README.md)  
Public release of RGB-D, LiDAR, IMU, and Pose recordings collected in real-world conditions  

</td>
<td width="40%">

<img src="./assets/Figure_2.png" alt="System Diagram" width="100%"/>

</td>
</tr>
</table>

---

## 3. Field Layout

<p align="center">
  <img src="./assets/Figure_3.png" alt="Experimental Field" style="width:100%;"/>
</p>

**Main Field Structure**  
- `Site 1`: Regular Canola (main target crop)  
- `Site 2`: Canola Genotype Trial  
- `Site 3`: Flax Trial  

---

## 4. Data Collection Protocol

### 📆 Collection Phases

| Phase   | Dates             | Frequency             | Purpose                                     |
|---------|-------------------|-----------------------|---------------------------------------------|
| Phase 1 | July 2–21         | 4× daily, 7 days/week | Active growth tracking & lighting variation |
| Phase 2 | July 22–Aug 1     | 2 sessions/week       | Slowed growth; less sampling                |

---

### 🧪 Site-wise Collection Frequency

| Site   | Description                  | Sessions/Day | Days/Week       | Period           |
|--------|------------------------------|--------------|-----------------|------------------|
| Site 1 | Main Canola Site             | 4            | 7               | July 2–21        |
|        |                              | 4            | 2               | July 22–Aug 1    |
| Site 2 | Canola Genotype Trial (Side) | 1            | 1–2 (selected)  | July 2–Aug 1     |
| Site 3 | Flax Trial (Side)            | 1            | 1–2 (selected)  | July 2–Aug 1     |

---

### 🛠 Field Conditions

- ❌ **Rainy days**: skipped  
- ✅ **Wet soil**: wooden boards used for UGV traversal  
- ☀️ **Lighting Diversity**:  
  - 06:00 (sunrise)  
  - 11:00 (late morning)  
  - 16:00 (afternoon)  
  - 21:00 (sunset)  


| Sun                        | Mon                        | Tue    | Wed                        | Thu                        | Fri    | Sat    |
|----------------------------|----------------------------|--------|----------------------------|----------------------------|--------|--------|
|                            |                            | **7/1**| **2**                      | **3**                      | **4**  | **5**  |
|                            |                            |        | S1 (4)<br>S2 (1)<br>S3 (1) | S1 (3)<br>S3 (1)           | S1 (3) | S1 (2) |
| **6**                      | **7**                      | **8**  | **9**                      | **10**                     | **11** | **12** |
| S1 (4)                     | S1 (4)                     | S1 (4) | S1 (4)                     | S1 (3)<br>S2 (1)<br>S3 (1) | S1 (4) | S1 (4) |
| **13**                     | **14**                     | **15** | **16**                     | **17**                     | **18** | **19** |
| S1 (4)<br>S2 (1)<br>S3 (1) | S1 (4)                     | S1 (4) | S1 (4)                     | S1 (4)<br>S2 (1)<br>S3 (1) | S1 (4) | S1 (4) |
| **20**                     | **21**                     | **22** | **23**                     | **24**                     | **25** | **26** |
| S1 (4)                     | S1 (2)<br>S2 (1)<br>S3 (1) | S1 (1) |                            | S1 (1)                     |        |        |
| **27**                     | **28**                     | **29** | **30**                     |**31**                      |**8/1** |        |
|                            | S1 (1)<br>S2 (1)<br>S3 (1) | S1 (1) | S1 (1)                     | S1 (1)                     |S1 (1)<br>S2 (1)<br>S3 (1)   |        |

---

## 5. Site Descriptions

### 🌼 Site 1: Main Canola Site
- **Dimensions**: 50 ft × 3 ft, 4 rows per plot, 9-inch spacing  
- **Planting**: June 1, 2025 → Emergence June 7  
- **Variety**: *InVigor L340PC*  
- **Flowering**: July 10, 2025  
- **Crop Duration**: 90–110 days  
- **Objective**: Provide a consistent reference for tracking temporal appearance changes of a single canola variety across growth stages and lighting conditions.  

---

### 🌼 Site 2: Canola Genotype Trial Site
- **Design**: 11 blocks × 44 genotypes  
- **Size**: 44 ft × 3 ft each  
- **Planting**: May 30, 2025  
- **Objective**: Capture morphological and structural variation by recording diverse genotypes planted in multiple distributed plots.  

---

### 🌿 Site 3: Flax Trial Site
- **Design**: 4 × 4 plots = 16 plots  
- **Size**: 8 ft × 3 ft each  
- **Planting**: May 30, 2025  
- **Variety**: *Gold ND*  
- **Duration**: 90–120 days  
- **Weed Control**:  
  - 3 blocks herbicide-sprayed by robot  
  - 1 block hand-weeded  
- **Objective**: Introduce complementary structural diversity through a different crop type and plot arrangement, including weed control treatments for comparative analysis.  

---

## 6. Data Structure

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
├── depth_npz_L/                  ← Depth (.npz) aligned to L_L camera
│   ├── 00000.npz
├── depth_npz_R/                  ← Depth (.npz) aligned to R_L camera
│   ├── 00000.npz
├── depth_png_L/                  ← Depth visualization (.png), aligned to L_L
│   ├── 00000.png
├── depth_png_R/                  ← Depth visualization (.png), aligned to R_L
│   ├── 00000.png
├── frame_L/                      ← PNG RGB frames from left ZED X
│   ├── L_00000.png               ← L_L: left sensor of left ZED X
│   ├── R_00000.png               ← L_R: right sensor of left ZED X
├── frame_R/                      ← PNG RGB frames from right ZED X
│   ├── L_00000.png               ← R_L: right sensor of left ZED X
│   ├── R_00000.png               ← R_R: right sensor of left ZED X
├── lidar/
│   ├── fov150                    ← LiDAR point clouds cropped to match ZED X stereo FoV (~150°)
│   │   ├── 00000.ply             ← LiDAR point cloud for frame 0
│   ├── fov360                    ← Full-range LiDAR point clouds (raw 360° FoV)
│   │   ├── 00000.ply             
│   ├── lidar_info.csv            ← Per-frame timestamp and IMU data from LiDAR
├── zed_info.csv                  ← Per-frame timestamp and IMU data from ZED L and R
├── pose_info.csv                 ← Per-frame timestamp and VIO Pose from ZED L and R
```

### CSV Format

#### `zed_info.csv`

| Column                       | Description                                           |
|------------------------------|-------------------------------------------------------|
| `L_frame_id`, `R_frame_id`   | Matched frame IDs from left/right ZED                 |
| `L_timestamp`, `R_timestamp` | Absolute timestamps (in seconds)                      |
| `relative_time`              | Time elapsed from the first ZED frame (starts at 0.0) |
| `L_*`, `R_*`                 | IMU data from each ZED (accel_x/y/z, gyro_x/y/z)      |

#### `pose_info.csv`

| Column                       | Description                                               |
|------------------------------|-----------------------------------------------------------|
| `L_frame_id`, `R_frame_id`   | Matched frame IDs from left/right ZED                     |
| `L_timestamp`, `R_timestamp` | Absolute timestamps (in seconds)                          |
| `L_*`, `R_*`                 | VIO Pose data from each ZED (trans_x/y/z, orien_x/y/z/w)  |

#### `lidar_info.csv`

| Column              | Description                                      |
|---------------------|--------------------------------------------------|
| `frame_id`          | Frame index aligned with ZED relative time       |
| `timestamp`         | Absolute timestamps (in seconds)                 |
| `accel_*`, `gyro_*` | IMU data from LiDAR at the corresponding time    |

---

## 7. Camera Calibration

### 📷 Left ZED X (4.0 mm)
- **Resolution**: 1920 × 1080 (FHD)

- **Intrinsic** (shared by both sensors):
```swift
fx = 1258.97, fy = 1258.97
cx =  916.48, cy =  553.83

```
- **Extrinsic** (Right → Left transform):
```swift
[ 1.000000  0.000000  0.000000  120.009026 ]
[ 0.000000  1.000000  0.000000    0.000000 ]
[ 0.000000  0.000000  1.000000    0.000000 ]
[ 0.000000  0.000000  0.000000    1.000000 ]
```

### 📷 Right ZED X (4.0 mm)
- **Resolution**: 1920 × 1080 (FHD)
- **Intrinsic** (shared by both sensors):
```swift
fx = 1261.83, fy = 1261.83
cx =  978.86, cy =  535.06
```
- **Extrinsic** (Right → Left transform):
```swift
[ 1.000000  0.000000  0.000000  120.212349 ]
[ 0.000000  1.000000  0.000000    0.000000 ]
[ 0.000000  0.000000  1.000000    0.000000 ]
[ 0.000000  0.000000  0.000000    1.000000 ]
```

---

## **📜 Citation**  
```tex
@article{jeong2025agrichrono,
  title={AgriChrono: A Multi-modal Dataset Capturing Crop Growth and Lighting Variability with a Field Robot},
  author={Jeong, Jaehwan and Vu, Tuan-Anh and Jony, Mohammad and Ahmad, Shahab and Rahman, Md. Mukhlesur and Kim, Sangpil and Jawed, M. Khalid},
  journal={arXiv preprint arXiv:2508.18694},
  year={2025},
}
```