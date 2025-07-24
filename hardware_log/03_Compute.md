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
> ✅ *ZED Link card can be directly connected and reliably stream at the desired resolution and FPS without bottlenecks*

---

### 💾 Internal Storage

- **Model**: Crucial P310 1TB 3D NAND Gen4 NVMe M.2 SSD  
- **Price**: $69.99  
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0DC8VPSHV)  
- **Status**: ✅ *Already owned*

#### Specifications
- **Interface**: PCIe Gen4 x4  
- **Form Factor**: M.2 2280  
- **Sequential Read**: Up to 7,100 MB/s  
> ✅ *1TB is sufficient — ~180–200 GB/hr per ZED at 15 FPS (SVO2)*  
> ✅ *I/O usage stays below 10%, so ultra-fast SSDs aren’t required*

---

### 💾 External Storage (Optional)

- **Model**: WD 8TB 3.5" HDD (exact model unknown)
- **Price**: Unknown
- **Purchase**: Unknown 
- **Status**: ✅ *Already owned*

#### Specifications
- **Capacity**: 8TB
> ✅ *Optional use — if data can be uploaded directly to a cloud server, external storage is unnecessary*  
> ✅ *If cloud upload is unavailable, this drive can serve as temporary backup storage*

---

### 📌 Selection Rationale

The compute system is optimized for **real-time RGB-D recording and on-device AI processing** during outdoor robotic field deployments:

- **Multi-Camera Performance**: The Jetson **Nano 8GB** could not sustain dual ZED streams at 15 FPS due to CPU and memory bottlenecks. The AGX Orin handles full-rate capture and processing reliably.  
- **High-Bandwidth Storage**: The Crucial P310 provides sufficient sequential speed for multi-channel RGB-D streaming without frame drops.  
- **Storage Capacity**: 1TB is sufficient — ~180–200 GB/hr per ZED (SVO2). Actual field sessions (e.g., in Fargo) rarely exceed 2 hours per run.  
- **Backup Readiness**: An external 8TB HDD is available for local backups when cloud upload is not feasible.  
- **ZED Compatibility**: Includes interface support for **ZED Duo Link capture cards**, ensuring seamless integration with multi-camera setups.

> This configuration balances robust field deployment with the throughput required for dense perception and data collection pipelines.

---

## ❌ Alternatives Considered

### 📌 Option: Samsung 990 PRO 2TB w/ Heatsink

**Device**: [Samsung 990 PRO 2TB Gen4 NVMe M.2 SSD (w/ Heatsink)](https://www.amazon.com/dp/B0BHJDY57J)  

**Pros**:  
- Excellent read/write performance (PCIe Gen4)  
- Large 2TB capacity  
- Built-in heatsink for thermal management  

**Cons**:  
- Expensive  
- Heatsink makes it physically incompatible with Jetson AGX Orin slot  
- Not owned  
- High I/O speed not essential due to SVO2 compression  

**Decision**: Rejected due to **price** and **physical incompatibility** with AGX Orin. Current workload (SVO2 recording) does not demand such high-speed storage.