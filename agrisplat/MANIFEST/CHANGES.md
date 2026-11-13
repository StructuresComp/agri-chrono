# Manifest

`patched.sha256`: SHA256 of every file except `MANIFEST/`, `datasets` and `outputs`
(`find . -type f ! -path './MANIFEST/*' ! -path './outputs/*' | sort`). Tag = first 8 hex digits of sha256(`patched.sha256`).

Changes relative to Octree-GS: NF default (`--visible_threshold 0`), CP (`utils/agrisplat_cp.py`), GR
(`utils/agrisplat_gr.py`), ADS (`utils/loss_utils.py:ads_loss`), their options (`AgriSplatParams`), seed, scene names
resolved under the data root, list-file train/test split, principal point, validation split, efficiency record
(training-loop time, peak VRAM from torch and NVML), `eval_bench.py`, `metrics_all.py`, `scripts/`; upstream
checkpointing is refused, the upstream code backup step is removed and `wandb` is imported only with `--use_wandb`.
File list: `NOTICE.md`.
