# 📡 Network & Communication Devices

## ✅ Selected Components

### 📶 Cellular Hotspot

- **Model**: Netgear Nighthawk M6 Pro (MR6500)
- **Price**: $212.24 
- **Purchase**: [Amazon](https://www.amazon.com/NETGEAR-Nighthawk-M6-Pro-International/dp/B0CKY7NBJ2)

#### Specifications
- **5G Bands**: Sub-6GHz + mmWave
- **Wi-Fi**: Wi-Fi 6E (up to 3.6 Gbps)
- **Ethernet**: 1x 2.5GbE LAN/WAN port
- **USB-C**: Charging & tethering (driverless network bridge)

> ✅ *Does not require IMEI registration or carrier certification — plug-and-play on major U.S. networks*  
> ✅ *Supports high-bandwidth uplink without USB-C power or driver dependencies*  
> ✅ *Hotspot mode enables simple remote access and streaming on the field*



- **Model**: Waveshare 5G Dongle Expansion Board (Quectel RM520N-GL, Qualcomm chipset)
- **Price**: $292.99  
- **Purchase**: [Amazon](https://www.amazon.com/waveshare-Expansion-Interface-RM520N-GL-Applicable/dp/B0DW8WR6SN)

---

### 📡 External Antennas

- **Model**: Proxicast 4x4 MIMO 5G Antenna (ANT-121-T44-B-02)  
- **Price**: $118.95
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0D56CR39YY)

#### Specifications
- 4x4 MIMO omnidirectional antenna
- **Frequency range**: 600 MHz – 6 GHz (Full Sub-6 band coverage)
- **Rated Gain**: 5–6 dBi per element (Sub-6GHz)
- 4x SMA connectors with 2ft coaxial cables  
> ✅ *Compatible with Quectel RM530N-GL (4x SMA ports for 4x4 MIMO)*  
> ✅ *Ideal for mobile platforms like the Scout robot, which frequently changes position and orientation*  

> 📌 **Note**: Originally purchased for use with a 4x4 MIMO-capable 5G Dongle, but due to IMEI certification issues, the dongle was replaced. The antenna was repurposed for the Netgear M6 Pro, using 2 of the 4 SMA connectors to enhance uplink stability.


---

### 🔌 USB Cable

- **Model**: 6 inch USB-C to USB-C 3.2 Gen 2×2, 100W PD Cable  
- **Price**: $8.89  
- **Purchase**: [Amazon](https://www.amazon.com/dp/B0DL62QKXP)

#### Specifications
- USB 3.2 Gen 2×2 (20 Gbps)
- Cable length: 15 cm (6 inches)  
> ✅ *Used to bridge Netgear hotspot to Jetson AGX Orin via 2.5GbE port*

---

### 📌 Selection Rationale

The Netgear Nighthawk M6 Pro (MR6500) was selected as the final networking solution for field operations based on the following priorities:

- **IMEI-free Activation**: Unlike the Quectel 5G dongle (RM520N-GL), which failed MEID/IMEI registration on major U.S. carriers, the M6 Pro requires no device-level activation, allowing plug-and-play use with standard SIM cards.
- **Driverless Setup**: Jetson AGX Orin connects via Wi-Fi or Ethernet without needing additional modem drivers, ensuring stable and OS-agnostic compatibility.
- **High Uplink Performance**: Provides upload speeds of up to 900 Mbps, sufficient for real-time video streaming and remote control during data collection missions.
- **Compact & Standalone**: Functions as a self-contained mobile hotspot, avoiding USB port congestion and thermal load on Jetson.
- **Stable Power Options**: Can operate via internal battery or external USB-C PD, with no dependence on the Jetson power supply.
- **Robust Connectivity**: Supports 2.5GbE wired fallback if wireless signal is weak or congested.

> This solution balances simplicity, reliability, and performance for long-term, high-bandwidth field connectivity—without the integration burden or certification issues of embedded modems.

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

### 📌 Option 1: Fixed Starlink Setup
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

### 📌 Option 2: Starlink Flat High Performance (Mounted on Robot)
**Device**: [Starlink Flat High Performance Kit](https://www.homedepot.com/pep/STARLINK-High-Performance-Kit-High-Speed-Low-Latency-Internet-02541005-HD/325986833?source=shoppingads&locale=en-US&pla&utm_source=google&utm_medium=vantage&utm_campaign=87951&utm_content=90528&mtc=SHOPPING-RM-RMP-GGL-D27L-Multi-NA-STARLINK-NA-PMAX-NA-NA-MK718549001-87951-NBR-30495-NA-VNT-FY25_Q1_Q4_VirtualSupply_Starlink_D27L_RM_ES_AON_BAUOpportunity&cm_mmc=SHOPPING-RM-RMP-GGL-D27L-Multi-NA-STARLINK-NA-PMAX-NA-NA-MK718549001-87951-NBR-30495-NA-VNT-FY25_Q1_Q4_VirtualSupply_Starlink_D27L_RM_ES_AON_BAUOpportunity-22542662595--&gclsrc=aw.ds&gad_source=1&gad_campaignid=22549081571&gbraid=0AAAAAolLu9_qNfx7bxZxqzdvmLn4Ei8bx&gclid=CjwKCAjwravBBhBjEiwAIr30VPmzia24cb2DFdjr_9D1GpXTH_Ex85mgO39OyZcjGzkNmcgwI3uNqBoCXKcQAvD_BwE)

**Pros**:
- Mobile-ready, stable satellite connection  

**Cons**:
- Extremely expensive  
- Heavy and bulky — nearly as large as Scout 2.0  

**Decision**: Unfeasible due to size, weight, and cost

---

### 📌 Option 3: LoRaWAN Gateway (NDSU Internal Network)

**Pros**:
- Long-range, low-power
- Utilizes pre-installed campus infrastructure  

**Cons**:
- Very low speed (0.3–50 Kbps) and high latency
- Not viable for streaming or real-time control  
- May require NDSU IT approval  

**Decision**: Unfeasible for interactive or responsive communication

---

### 📌 Option 4: Quectel RM530N-GL Module

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

### 📌 Option 5: Quectel RM520N-GL Module

**Pros**:
- Sub-6GHz 5G modem based on Qualcomm Snapdragon X62
- Uplink speeds up to 900 Mbps, with low power draw (~4–6W)
- Advertised as pre-certified for major global carriers like Verizon, AT&T, T-Mobile

**Cons**:
- Despite the advertised pre-certification, actual deployment resulted in IMEI registration errors
- Required the user to contact the carrier via the vendor to manually register the IMEI
- This process proved cumbersome and complex, with no guaranteed timeline
- These issues led to repeated connection failures

**Decision**: Due to unresolved IMEI registration issues and repeated failures in the field, this device was ultimately replaced by the Netgear M6 Pro hotspot, which does not require IMEI approval for activation.

---

## 📝 Final Justification

The Netgear Nighthawk M6 Pro was selected as the final field networking solution due to its:

- IMEI-free operation, which eliminates the risk of carrier registration issues faced with embedded 5G dongles.
- Plug-and-play compatibility with U.S. carriers (e.g., Verizon, T-Mobile, AT&T) using standard SIM cards.
- Driverless Ethernet and Wi-Fi bridging, enabling seamless integration with Jetson AGX Orin without software or firmware dependencies.
- High uplink capacity (~900 Mbps), sufficient for live video streaming, telemetry, and remote access.
- Stable dual power options (internal battery or USB-C PD), allowing untethered use or external power when needed.
- Compact and mobile form factor, suitable for mounting or stowing within the robot platform during deployment.

> This hotspot solution directly addressed the practical deployment needs in Fargo's dynamic field environment, ensuring stable 5G uplink without certification hurdles or complex setup procedures.