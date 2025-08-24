# 📊 Benchmark & Evaluation

We introduce a **novel benchmark** using the [AgriChrono dataset](../README.md) to evaluate state-of-the-art Gaussian Splatting methods under **real-world agricultural challenges** such as **lighting variance** and **growth span**.

---

## 🌱 Dataset & Protocol

- **Dataset**: 60-second monocular RGB sequences (900 frames @ 15 FPS, resized to 512×288)  
- **Segmentation**: Each sequence divided into **10 batches** (90 frames each)  
- **Training Sets**:
  - 15 FPS → 90 images
  - 10 FPS → 60 images
  - 5 FPS → 30 images
  - 3 FPS → 18 images  
- **Evaluation**:
  - **Training Views**: 15 FPS (same poses)
  - **Novel Views**: 10, 5, 3 FPS (unseen poses only)  
- **Camera Poses**: Estimated using **VGGT** (preferred over COLMAP due to dynamic scene difficulty)

<p align="center">
  <img src="../figure/Figure_6_v2.pdf" width="80%">
</p>  

---

## 🔑 Benchmark Settings

We define four training–rendering configurations:

1. **Setting 1**: Train 15 FPS → Render 15 FPS (training views)  
2. **Setting 2**: Train 10 FPS → Render 5 FPS  
3. **Setting 3**: Train 5 FPS → Render 10 FPS  
4. **Setting 4**: Train 3 FPS → Render 12 FPS  

---

## ☀️ Benchmark Challenges

- **Lighting Variance**  
  - Same-day captures at 06:00, 11:00, 16:00, and 21:00  
  - Tests robustness to strong illumination changes  

- **Growth Span**  
  - Morning captures across three growth stages (Day 6, 13, 20)  
  - Evaluates adaptation to temporal morphological change  

---

## 🧪 Methods & Metrics

- **Methods Evaluated**  
  - Four Gaussian Splatting baselines: [CUT3R](https://…), [FAST3R](https://…), [MASt3R-SLAM](https://…), [InstantSplat](https://…)  
- **Metrics**  
  - **PSNR**, **SSIM** (quantitative fidelity)  
  - Qualitative comparisons provided in `figures/`

> Even training views achieved PSNR only in the low 30s (vs. ~40+ expected indoors), underscoring the **difficulty of real-field data**.  
> Novel-view performance was significantly lower and varied strongly with lighting and growth stages.  

---

## 📂 Reproduction

To reproduce benchmark results:

```bash
# Example: Training CUT3R on AgriChrono (Site 1, Day 6, 15 FPS)
bash scripts/run_cut3r.sh --data /path/to/agri-chrono/site1/day6 --fps 15

# Evaluation against ground truth
python evaluate.py \
  --pred ./outputs/cut3r/day6/15fps \
  --gt ./agri-chrono/site1/day6/gt \
  --metrics psnr ssim
