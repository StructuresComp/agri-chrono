# 💾 AgriChrono Dataset

<p align="center">
  <img src="../assets/Figure_4.png" alt="AgriChrono Dataset Properties" style="width:100%;"/>
</p>

This section provides access to the datasets collected with the **AgriChrono platform**, covering diverse **outdoor agricultural conditions** across multiple sites, times of day, and crop growth stages.

---

## 1. Dataset Statistics

| **Site**              | **# Sessions** | **FPS** | **Duration (s)** | **# Samples** | **Size** |
|:----------------------|:--------------:|:-------:|:----------------:|:-------------:|:--------:|
| **Site 1 (CW)**       | 80             | 14.7    | 18,834           | 276,656       | 6.8 TB   |
| **Site 1 (CCW)**      | 80             | 14.7    | 19,098           | 282,919       | 6.9 TB   |
| **Site 2**            | 7              | 13.1    | 10,235           | 129,088       | 3.2 TB   |
| **Site 3**            | 8              | 14.6    | 2,879            | 42,097        | 1.1 TB   |
| **Total**             | **175**        | **14.3**| **51,046**       | **730,760**   | **18 TB**|

Each synchronized multi-modal sample contains:  
- **4 RGB images**  
- **2 depth maps**  
- **1 LiDAR scan**

---

## 2. Available Downloads

- 🌱 [**Samples**](https://ucla.box.com/s/jo0glrpvt9u6ytioleek12dc1wo74ma2)  
  Original-resolution subset for high-quality experiments.  

- 🖼️ [**Only RGB (Stereo)**](https://ucla.box.com/s/t77te4x3s8nkqale9k8nixe6q9nxo2ii)  
  - **Site 1**: Direction-specific (CW → right ZED only, CCW → left ZED only)  
  - **Sites 2 & 3**: Both left and right ZED sensors included  
  - Contains **only stereo RGB images**, without depth or LiDAR  

- 🌾 [**Full AgriChrono Dataset (18TB)**](https://ucla.box.com/s/22nonjreia1m16gw9mbjup6f538y4fvo)  

- 📊 [**Benchmark Dataset**](../benchmark/README.md)  
  Novel View Synthesis benchmark on AgriChrono across seven scenarios featuring lighting variance and growth span.

---

## 3. Sample Contents

> **Note**: The sample data is organized as follows. Of these, 400 samples from the Growth Span and Lighting Variance subsets were utilized for the benchmark.

1. **Field Diversity**  
   - Sites: Site 1 (*Clockwise / Counter-Clockwise*), Site 2, Site 3
   - Captures: July 21, 4 PM  
   - Files: `[Site]_RGB.mp4`, `[Site]_Depth.mp4`, `[Site]_Lidar.mp4`, plus `.tar.gz` archives  

2. **Growth Span**  
   - Weeks: Day 6, Day 13, Day 20 (captured at 6 AM)  
   - Files: `[Week]_RGB.mp4`, `[Week]_Depth.mp4`, `[Week]_Lidar.mp4`, plus `.tar.gz` archives  

3. **Lighting Variance**  
   - Times: **06:00, 11:00, 16:00, 21:00**  
   - Captures: July 19, Site 1 (CCW direction)  
   - Files: `[Time]_RGB.mp4`, `[Time]_Depth.mp4`, `[Time]_Lidar.mp4`, plus `.tar.gz` archives  
   
---

## **📜 Citation**  
```tex
@article{jeong2025agrichrono,
  title={AgriChrono: A Longitudinal Dataset and Benchmark for Novel-View Synthesis of Field-Grown Crops},
  author={Jeong, Jaehwan and Vu, Tuan-Anh and Jony, Mohammad and Ahmad, Shahab and Rahman, Md. Mukhlesur and Kim, Sangpil and Jawed, M. Khalid},
  journal={arXiv preprint arXiv:2508.18694},
  year={2025},
}
```