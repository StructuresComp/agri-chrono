"""Render the test views to <model>/bench/ and score them with nerfbaselines 1.2.12 (results.json)."""
import os, json, time
import numpy as np, torch, torchvision
from argparse import ArgumentParser
from arguments import ModelParams, PipelineParams, get_combined_args
from scene import Scene
from gaussian_renderer import render, prefilter_voxel, GaussianModel


def n_levels(gaussians):
    """Number of octree levels (`levels` is not restored by load_ply_sparse_gaussian)."""
    return max(int(getattr(gaussians, "levels", 0) or 0), int(gaussians.get_level.max().item()) + 1)


def build_model(dataset):
    return GaussianModel(
        dataset.feat_dim, dataset.n_offsets, dataset.fork, dataset.use_feat_bank, dataset.appearance_dim,
        dataset.add_opacity_dist, dataset.add_cov_dist, dataset.add_color_dist, dataset.add_level,
        dataset.visible_threshold, dataset.dist2level, dataset.base_layer, dataset.progressive, dataset.extend)


def main():
    parser = ArgumentParser(description="Test-view evaluation", allow_abbrev=False)
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    parser.add_argument("--iteration", default=-1, type=int)
    parser.add_argument("--ape", default=-1, type=int)
    parser.add_argument("--out_name", default="bench", type=str)
    parser.add_argument("--split", default="test", choices=["test", "train", "val"],
                        help="test: test frames; train: how well the model fits its own training frames; "
                             "val: held-out train frames of a --val_holdout run (hyper-parameter selection)")
    parser.add_argument("--allow_local_metrics", action="store_true",
                        help="permit the non-nerfbaselines fallback (not comparable to nerfbaselines 1.2.12 scores)")
    args = get_combined_args(parser)
    dataset = model.extract(args)
    pipe = pipeline.extract(args)
    try:
        import nerfbaselines
        from nerfbaselines.evaluation import compute_metrics
        nb_version = getattr(nerfbaselines, "__version__", "unknown")
        if nb_version != "1.2.12":
            raise RuntimeError(f"nerfbaselines {nb_version} installed; the reported metrics use 1.2.12 "
                               f"(pip install --no-deps nerfbaselines==1.2.12)")
        backend = f"nerfbaselines-{nb_version}"
    except Exception as e:
        if not args.allow_local_metrics:
            raise RuntimeError(f"nerfbaselines metrics unavailable ({e}); refusing to silently change the metric. "
                               f"Pass --allow_local_metrics to use the local fallback (not comparable to the paper).")
        print("[warn] nerfbaselines unavailable, using LOCAL metrics (not comparable to nerfbaselines 1.2.12 scores):", e)
        backend = "local"
        from utils.loss_utils import ssim as _ssim
        import lpips as _lpips
        _lp_alex = _lpips.LPIPS(net='alex').cuda(); _lp_vgg = _lpips.LPIPS(net='vgg').cuda()

    def score(p, g, pred_t, gt_t):
        if backend.startswith("nerfbaselines"):
            return {k: float(v) for k, v in compute_metrics(p[None], g[None], run_lpips_vgg=True).items()}
        mse = float(((p - g) ** 2).mean())
        return {"psnr": 10 * np.log10(1 / max(mse, 1e-12)), "ssim": float(_ssim(pred_t[None], gt_t[None])), "mse": mse,
                "lpips": float(_lp_alex(pred_t[None] * 2 - 1, gt_t[None] * 2 - 1)),
                "lpips_vgg": float(_lp_vgg(pred_t[None] * 2 - 1, gt_t[None] * 2 - 1))}

    with torch.no_grad():
        gaussians = build_model(dataset)
        scene = Scene(dataset, gaussians, load_iteration=args.iteration, shuffle=False)
        gaussians.eval()
        bg = torch.tensor([1, 1, 1] if dataset.white_background else [0, 0, 0], dtype=torch.float32, device="cuda")
        if args.split == "train":
            views = scene.getTrainCameras()
        else:
            views = [v for v in scene.getTestCameras() if getattr(v, 'is_val', False) == (args.split == "val")]
        assert views, f'no {args.split} views'
        views = sorted(views, key=lambda v: v.image_name)
        print(f"[AgriSplat] metrics backend={backend}")

        base = {"test": args.out_name, "train": f"{args.out_name}_trainviews", "val": f"{args.out_name}_val"}[args.split]
        out_dir = os.path.join(dataset.model_path, base)
        os.makedirs(os.path.join(out_dir, "color"), exist_ok=True)
        os.makedirs(os.path.join(out_dir, "gt-color"), exist_ok=True)
        per_image, times = [], []
        for view in views:
            torch.cuda.synchronize(); t0 = time.time()
            gaussians.set_anchor_mask(view.camera_center, scene.loaded_iter, view.resolution_scale)
            vis = prefilter_voxel(view, gaussians, pipe, bg)
            pkg = render(view, gaussians, pipe, bg, visible_mask=vis, ape_code=args.ape)
            torch.cuda.synchronize(); times.append(time.time() - t0)
            # quantise exactly like torchvision.save_image, so the score equals scoring the saved PNG
            pred = torch.clamp(pkg["render"], 0, 1).mul(255).add(0.5).clamp(0, 255).floor().div(255)
            gt = view.original_image[0:3].cuda()
            torchvision.utils.save_image(pred, os.path.join(out_dir, "color", view.image_name + ".png"))
            torchvision.utils.save_image(gt, os.path.join(out_dir, "gt-color", view.image_name + ".png"))
            p = pred.permute(1, 2, 0).cpu().numpy().astype(np.float32)
            g = gt.permute(1, 2, 0).cpu().numpy().astype(np.float32)
            rec = score(p, g, pred, gt)
            rec["name"] = view.image_name
            per_image.append(rec)
            print(f"{view.image_name}: psnr={rec['psnr']:.3f} ssim={rec['ssim']:.4f} lpips={rec['lpips']:.4f}")

        keys = sorted({k for r in per_image for k in r} - {"name"})
        mean, counts = {}, {}
        for k in keys:
            vals = [r[k] for r in per_image if k in r and np.isfinite(r[k])]
            if vals:
                mean[k] = float(np.mean(vals)); counts[k] = len(vals)
        lvl = gaussians.get_level.view(-1).long()
        mean["anchor_levels"] = {int(L): int((lvl == L).sum()) for L in range(n_levels(gaussians))}
        mean["render_time_s"] = float(np.mean(times)); mean["n_test"] = len(per_image)
        mean["iteration"] = scene.loaded_iter
        mean["n_anchors"] = int(gaussians.get_anchor.shape[0])
        mean["metrics_backend"] = backend
        mean["split"] = args.split
        with open(os.path.join(out_dir, "results.json"), "w") as f:
            json.dump({"mean": mean, "counts": counts, "per_image": per_image}, f, indent=2)
        show = {k: round(mean[k], 4) for k in ("psnr", "ssim", "lpips", "lpips_vgg") if k in mean}
        print(f"\n== MEAN ({backend}):", json.dumps(show), "| n_anchors", mean["n_anchors"],
              "| levels", mean["anchor_levels"], "\n")


if __name__ == "__main__":
    main()
