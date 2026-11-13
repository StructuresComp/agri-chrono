#!/bin/bash
# Usage: bash scripts/run_all.sh [nf|cp|cpgr|ads|full] [train.py options]   (default full, seed 0)
# Trains and scores every scenario found under the data root; scenes with outputs/<scene>/<variant>/results.json are skipped.
set -euo pipefail
VARIANT=${1:-full}; [ $# -gt 0 ] && shift
REPO=$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)
ROOT=${AGRISPLAT_DATA:-$REPO/datasets}
for SCENE in Table1/06 Table1/11 Table1/16 Table1/21 Table2/Week1 Table2/Week2 Table2/Week3; do
  [ -d "$ROOT/$SCENE" ] || { echo "skip $SCENE: not in $ROOT"; continue; }
  [ -f "$REPO/outputs/$SCENE/$VARIANT/results.json" ] && { echo "skip $SCENE: done"; continue; }
  bash "$REPO/scripts/train_eval.sh" "$VARIANT" "$SCENE" 0 --data_root "$ROOT" "$@"
done
python "$REPO/metrics_all.py" --summary --variant "$VARIANT"   # also writes outputs/summary_$VARIANT.csv
