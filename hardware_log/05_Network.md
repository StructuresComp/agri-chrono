# 📡 Network & Communication Devices

## ✅ Selected Components

### 📶 5G Dongle

- **Model**: Waveshare 5G Dongle Expansion Board (Quectel RM520N-GL, Qualcomm chipset)
- **Price**: $292.99  
- **Purchase**: [Amazon](https://www.amazon.com/waveshare-Expansion-Interface-RM520N-GL-Applicable/dp/B0DW8WR6SN)

#### Specifications
- Quectel RM520N-GL: supports Sub-6GHz 5G bands
- **Peak Speeds (Sub-6GHz)**:
  - **5G NR SA**: up to **2.4 Gbps (DL)** / **900 Mbps (UL)**
  - **5G NR NSA**: up to **3.4 Gbps (DL)** / **550 Mbps (UL)**
- **MIMO Support**:
  - Sub-6GHz: 4x4 MIMO (DL), 2x2 MIMO (UL)
- 4x SMA antenna connectors for external high-gain antennas
- USB-C 3.2 Gen 2 interface (10 Gbps), converted from M.2 Key B  
> ✅ *Compatible with Jetson AGX Orin (USB-C 3.2 Gen 2, 10 Gbps, x1 lane)*  
> ✅ *Pre-certified for major carriers including Verizon, AT&T, T-Mobile, NTT DOCOMO, KT, and others*

---

### 📡 External Antennas

- **Model**: Proxicast 4x4 MIMO 5G Antenna (ANT-121-T44-B-02)  
- **Price**: $118.95
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0D56CR39YY)

#### Specifications
- 4x4 MIMO omnidirectional antenna
- Frequency range: 600 MHz – 6 GHz (Full Sub-6 band coverage)
- **Rated Gain**: 5–6 dBi per element (Sub-6GHz)
- 4x SMA connectors with 2ft coaxial cables  
> ✅ *Compatible with Quectel RM530N-GL (4x SMA ports for 4x4 MIMO)*  
> ✅ *Ideal for mobile platforms like the Scout robot, which frequently changes position and orientation*

---

### 🔌 USB Cable

- **Model**: 6 inch USB-C to USB-C 3.2 Gen 2×2, 100W PD Cable  
- **Price**: $8.89  
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0DL62QKXP)

#### Specifications
- USB 3.2 Gen 2×2 (20 Gbps)
- Cable length: 15 cm (6 inches)  
> ✅ *Ensures stable 10 Gbps connection between the 5G Dongle and Jetson AGX Orin via USB-C 3.2 Gen 2*

---

### 📌 Selection Rationale

The 5G Dongle + External Antenna setup was chosen based on the following priorities:

- **Uplink Performance**: Real-time video streaming is the primary task, and this setup supports uplink speeds of up to 900 Mbps—sufficient for high-bandwidth tasks and comparable to the best available solutions.
- **Deployment Environment**: Designed for use in North Dakota (Fargo), where mobile signal quality can vary; the external 4x4 MIMO antenna ensures consistent connectivity on moving platforms.
- **Carrier Compatibility**: The Quectel RM520N-GL module is pre-certified for major global carriers including Verizon, AT&T, T-Mobile, NTT DOCOMO, KT, and others—eliminating the need for additional certification or configuration.
- **Power Efficiency**: The dongle operates directly via USB-C without requiring any external power supply, consuming only ~4–6W during active operation.
- **Compact and Modular**: The setup is lightweight, space-efficient, and easy to integrate into the Scout robot platform.
- **Stability and Reliability**: The Quectel RM530N-GL module, based on Qualcomm’s industrial-grade 5G chipset, is known for stable performance in embedded and edge computing environments.
- **Cost-effectiveness**: Total cost (dongle + antenna + high-speed cable) remains under **$500**, offering significantly better value than more complex solutions like Starlink HP or industrial hotspots.

Considering uplink needs, field robustness, and overall integration simplicity, this configuration was selected as the most practical and reliable solution for real-time mobile networking.

---

## 📊 Signal Measurements in Fargo

- **5G**: -99 dBm (within standard performance range)  
- **LTE**: -108 dBm (usable but unstable)

> 📌 *These values were obtained in advance using a regular smartphone prior to finalizing the hardware setup. Measurements do not reflect performance with the selected 5G dongle and antenna.*

### ⚙️ Uplink & Downlink Speed by Carrier (Fargo, ND)

| **Carrier**   | **Avg. Download** | **Avg. Upload** | **Summary** |
|---------------|-------------------|------------------|-------------|
| **Verizon**   | ~142.5 Mbps       | ~22.2 Mbps       | Highest average download speed in Fargo |
| **T-Mobile**  | ~105.1 Mbps       | ~12.2 Mbps       | Solid average performance on both DL and UL |
| **AT&T**      | ~52.6 Mbps        | ~16.6 Mbps       | Slower download, moderate upload speed |

> 📌 *Data based on real-world average speed measurements for Sub-6GHz 5G and LTE connections in Fargo, ND. Sources include [nPerf](https://www.nperf.com/en/map/US/5052016.Fargo/3.T-Mobile/signal/), [BestNeighborhood.org](https://bestneighborhood.org/fastest-internet-fargo-nd/), and [CoverageMap.com](https://coveragemap.com/), as of 2024.*

---

## ❌ Alternatives Considered

### :pushpin: Option 1: Fixed Starlink Setup
**Device**: [Starlink Mini](https://www.walmart.com/ip/STARLINK-Mini-Kit-AC-Dual-Band-Wi-Fi-System-White/13168716173?classType=REGULAR&athbdg=L1103&from=/search&adid=22222222220220085369&wmlspartner=wmtlabs&veh=sem&vtcWeb=Z2fbYWq8ZsDIYOxlA5Cf8Q&expiryTime=1747686365877&c=mWebSmartBanner) or [Standard Kit](https://www.walmart.com/ip/Standard-Kit-High-Speed-Low-Latency-Internet-Latest-Model/5597651559?classType=REGULAR&athbdg=L1200&adsRedirect=true)

**Pros**:
- High throughput and low latency  
- Global coverage  

**Cons**:
- Requires dedicated power  
- Needs daily manual setup and teardown  
- Setup must be handled by NDSU students on-site  

**Decision**: Rejected due to operational burden during fieldwork

---

### :pushpin: Option 2: Starlink Flat High Performance (Mounted on Robot)
**Device**: [Starlink Flat High Performance Kit](https://www.homedepot.com/pep/STARLINK-High-Performance-Kit-High-Speed-Low-Latency-Internet-02541005-HD/325986833?source=shoppingads&locale=en-US&pla&utm_source=google&utm_medium=vantage&utm_campaign=87951&utm_content=90528&mtc=SHOPPING-RM-RMP-GGL-D27L-Multi-NA-STARLINK-NA-PMAX-NA-NA-MK718549001-87951-NBR-30495-NA-VNT-FY25_Q1_Q4_VirtualSupply_Starlink_D27L_RM_ES_AON_BAUOpportunity&cm_mmc=SHOPPING-RM-RMP-GGL-D27L-Multi-NA-STARLINK-NA-PMAX-NA-NA-MK718549001-87951-NBR-30495-NA-VNT-FY25_Q1_Q4_VirtualSupply_Starlink_D27L_RM_ES_AON_BAUOpportunity-22542662595--&gclsrc=aw.ds&gad_source=1&gad_campaignid=22549081571&gbraid=0AAAAAolLu9_qNfx7bxZxqzdvmLn4Ei8bx&gclid=CjwKCAjwravBBhBjEiwAIr30VPmzia24cb2DFdjr_9D1GpXTH_Ex85mgO39OyZcjGzkNmcgwI3uNqBoCXKcQAvD_BwE)

**Pros**:
- Mobile-ready, stable satellite connection  

**Cons**:
- Extremely expensive  
- Heavy and bulky — nearly as large as Scout 2.0  

**Decision**: Unfeasible due to size, weight, and cost

---

### :pushpin: Option 3: Cellular Hotspot (Netgear Nighthawk M6 Pro)
**Device**: [Netgear MR6550 (M6 Pro)](https://www.amazon.com/NETGEAR-Nighthawk-Unlocked-International-Countries/dp/B0C2ZP2DXH)

**Pros**:
- Supports 5G mmWave (up to 8 Gbps downlink)
- Wi-Fi 6E and 2.5GbE port support  

**Cons**:
- **Uplink speed** still around ~900 Mbps — similar to dongle
- Consumes more power (~10–12W vs. 4–6W for dongle)
- User reviews report frequent disconnections  

**Decision**: Rejected due to equivalent uplink speed, higher power draw, and reliability issues

---

### :pushpin: Option 4: LoRaWAN Gateway (NDSU Internal Network)

**Pros**:
- Long-range, low-power
- Utilizes pre-installed campus infrastructure  

**Cons**:
- Very low speed (0.3–50 Kbps) and high latency
- Not viable for streaming or real-time control  
- May require NDSU IT approval  

**Decision**: Unfeasible for interactive or responsive communication

---

### :pushpin: Option 5: Quectel RM530N-GL Module

**Pros**:
- High-performance Qualcomm-based 5G modem  
- Supports both Sub-6GHz and mmWave  
- Industrial-grade stability and speed  

**Cons**:
- **No out-of-the-box carrier certification** for major U.S. networks (e.g., Verizon, AT&T, T-Mobile)  
- Requires end-user to undergo **separate carrier approval process**  
- Risk of **incompatibility or throttling** in real-world deployment without certification  

**Decision**: Rejected due to carrier compatibility limitations and lack of pre-certification, which pose risks for reliable field connectivity.

---

## 📝 Final Justification

Although Starlink provides unmatched stability, it was rejected due to **logistical complexity**, **cost**, and **form factor**.  
The Netgear M6 Pro hotspot—while high-performing—offered **no uplink advantage**, consumed **more power**, had reported **stability issues**, and came at a **significantly higher cost**.

Given that only one Jetson device requires internet access, the **Waveshare 5G Dongle + MIMO Antennas** was chosen as the **most efficient, compact, and reliable** uplink solution for field streaming in North Dakota test environments.
