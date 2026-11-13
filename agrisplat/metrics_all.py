"""The seven paper metrics of the saved test renders: PSNR_W, SSIM_W, LPIPS_W (whole image) and SSIM_C, LPIPS_C, GER_C,
EdgeF_C (Canola region = yellow pixels of the masks), written to outputs/<scene>/<variant>/results.json; --summary tabulates."""
import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

YELLOW_BGR = np.array([55, 250, 250], np.uint8)
KEYS = ("PSNR_W", "SSIM_W", "LPIPS_W", "SSIM_C", "LPIPS_C", "GER_C", "EdgeF_C")
REPO = Path(__file__).resolve().parent


def rgb(path):
    return np.ascontiguousarray(cv2.imread(str(path))[:, :, ::-1]).astype(np.float32) / 255


def luminance(x):
    return (0.299 * x[:, :, 0] + 0.587 * x[:, :, 1] + 0.114 * x[:, :, 2]).astype(np.float32)


def sobel_energy(x):
    y = luminance(x)
    gx, gy = cv2.Sobel(y, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(y, cv2.CV_32F, 0, 1, ksize=3)
    return gx * gx + gy * gy


def canny(x):
    y8 = np.clip(np.round(luminance(x) * 255), 0, 255).astype(np.uint8)
    return cv2.Canny(cv2.GaussianBlur(y8, (0, 0), 1.0), 30, 90, L2gradient=True) > 0


def edge_counts(p, g, roi):
    """(render edges, matched render edges, GT edges, matched GT edges) inside roi, exact Euclidean 2 px tolerance"""
    er, eg = canny(p) & roi, canny(g) & roi
    dg = cv2.distanceTransform((~eg).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    dr = cv2.distanceTransform((~er).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return np.array([er.sum(), (er & (dg <= 2)).sum(), eg.sum(), (eg & (dr <= 2)).sum()], np.float64)


def score(bench, scene_dir, masks):
    import torch
    import lpips
    from nerfbaselines.metrics import ssim
    lpips_alex = lpips.LPIPS(net="alex", spatial=True, verbose=False).eval()
    names = sorted(Path(n.strip()).stem for n in (scene_dir / "test_list.txt").read_text().splitlines() if n.strip())
    W = {"psnr": [], "ssim": [], "lpips": []}
    C = dict(n=0, frames=0, ssim=0.0, ssim_n=0, lpips=0.0, er=0.0, eg=0.0, edges=np.zeros(4))
    for name in names:
        p, g = rgb(bench / "color" / f"{name}.png"), rgb(bench / "gt-color" / f"{name}.png")
        with torch.no_grad():
            lp = lpips_alex(torch.from_numpy(p).permute(2, 0, 1)[None] * 2 - 1,
                            torch.from_numpy(g).permute(2, 0, 1)[None] * 2 - 1)[0, 0].numpy()
        W["psnr"].append(10 * np.log10(1 / max(float(((p - g) ** 2).mean()), 1e-12)))
        W["ssim"].append(float(ssim(g, p)))
        W["lpips"].append(float(lp.mean()))
        if not masks.is_dir():
            continue
        roi = np.all(cv2.imread(str(masks / f"{name}.png")) == YELLOW_BGR, axis=2)
        if not roi.any():
            continue
        C["n"] += int(roi.sum())
        C["frames"] += 1
        inner = roi[5:-5, 5:-5]                                   # the SSIM map covers the valid interior only
        C["ssim"] += float(ssim(g, p, reduce=False).mean(axis=-1)[inner].sum(dtype=np.float64))
        C["ssim_n"] += int(inner.sum())
        C["lpips"] += float(lp[roi].sum())
        C["er"] += float(sobel_energy(p)[roi].sum())
        C["eg"] += float(sobel_energy(g)[roi].sum())
        C["edges"] += edge_counts(p, g, roi)
    out = {"PSNR_W": float(np.mean(W["psnr"])), "SSIM_W": float(np.mean(W["ssim"])), "LPIPS_W": float(np.mean(W["lpips"])),
           "n_test": len(names)}
    if C["n"]:
        ner, nerm, neg, negm = C["edges"]
        P, R = nerm / ner, negm / neg
        out.update(SSIM_C=C["ssim"] / C["ssim_n"], LPIPS_C=C["lpips"] / C["n"], GER_C=C["er"] / C["eg"],
                   EdgeF_C=float(2 * P * R / (P + R)), n_region_frames=C["frames"])
    return out


def summary(outputs, variant):
    """Per-scene rows and the mean of the seven metrics, training time (min) and NVML peak VRAM (GB); also written as CSV."""
    cols = KEYS + ("Time_min", "VRAM_GB")
    rows = []
    for f in sorted(outputs.glob(f"*/*/{variant}/results.json")):
        r = json.loads(f.read_text())
        r["Time_min"], r["VRAM_GB"] = r["train_loop_s"] / 60, r["peak_vram_nvml_gb"]
        rows.append([str(f.parent.parent.relative_to(outputs))] + [r.get(k) for k in cols])
    if rows:
        rows.append(["Mean"] + [None if any(x[i] is None for x in rows) else float(np.mean([x[i] for x in rows]))
                                for i in range(1, len(cols) + 1)])
    fmt = lambda v: "-" if v is None else f"{v:.4f}"
    csv = [",".join(("scene",) + cols)] + [",".join([r[0], *map(fmt, r[1:])]) for r in rows]
    (outputs / f"summary_{variant}.csv").write_text("\n".join(csv) + "\n")
    lines = ["| scene | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    return "\n".join(lines + [f"| {r[0]} | " + " | ".join(map(fmt, r[1:])) + " |" for r in rows])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", help="scene name (e.g. Table2/Week3) or folder")
    ap.add_argument("--variant", default="full")
    ap.add_argument("--data_root", default=os.environ.get("AGRISPLAT_DATA", str(REPO / "datasets")))
    ap.add_argument("--mask_root", help="masks at <mask_root>/<scene>/<frame>.png (default <scene folder>/mask)")
    ap.add_argument("--model_dir", type=Path, help="default outputs/<scene>/<variant>")
    ap.add_argument("--out", type=Path, help="default <model_dir>/results.json")
    ap.add_argument("--summary", action="store_true", help="tabulate outputs/*/*/<variant>/results.json")
    a = ap.parse_args()
    if a.summary:
        print(summary(REPO / "outputs", a.variant))
        sys.exit()
    scene_dir = Path(a.scene) if Path(a.scene).is_dir() else Path(a.data_root) / a.scene
    masks = Path(a.mask_root) / a.scene if a.mask_root else scene_dir / "mask"
    model_dir = a.model_dir or REPO / "outputs" / a.scene / a.variant
    result = score(model_dir / "bench", scene_dir, masks)
    eff = json.loads((model_dir / "train_efficiency.json").read_text())
    result.update({k: eff[k] for k in ("train_loop_s", "peak_vram_nvml_gb", "peak_vram_gb", "n_anchors", "gpu")})
    result["train_loop_mmss"] = "%d:%02d" % divmod(round(eff["train_loop_s"]), 60)
    print(json.dumps(result, indent=1))
    (a.out or model_dir / "results.json").write_text(json.dumps(result, indent=1))
