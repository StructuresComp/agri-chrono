#!/bin/bash
# Usage: bash scripts/train_eval.sh nf|cp|cpgr|ads|full SCENE [SEED [train.py options]]
#   SCENE is a folder or a name under the data root (--data_root, $AGRISPLAT_DATA or ./datasets), e.g. Table2/Week3.
#   Output: outputs/<SCENE>/<variant>[_s<SEED>]/ (results.json = all metrics). Environment: ITERATIONS (default 40000).
set -euo pipefail

VARIANT=$1; SCENE=$2; SEED=${3:-0}
shift 2; if [ $# -gt 0 ]; then shift; fi
ITER=${ITERATIONS:-40000}
REPO=$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)

case "$VARIANT" in
  nf) METHOD=(--cp 0 --gr 0 --ads 0) ;;
  cp) METHOD=(--cp 1 --gr 0 --ads 0) ;;
  cpgr) METHOD=(--cp 1 --gr 1 --ads 0) ;;
  ads) METHOD=(--cp 0 --gr 0 --ads 1) ;;
  full) METHOD=(--cp 1 --gr 1 --ads 1) ;;
  *) echo "unknown VARIANT $VARIANT (nf | cp | cpgr | ads | full)" >&2; exit 2 ;;
esac
ROOT=${AGRISPLAT_DATA:-$REPO/datasets}
ARGS=("$@")
for i in "${!ARGS[@]}"; do [ "${ARGS[$i]}" = --data_root ] && ROOT=${ARGS[$((i + 1))]}; done
SCENE_DIR=$SCENE; [ -d "$SCENE_DIR" ] || SCENE_DIR=$ROOT/$SCENE
[ -d "$SCENE_DIR" ] || { echo "scene not found: $SCENE_DIR" >&2; exit 2; }
SCENE_DIR=$(cd "$SCENE_DIR" && pwd)
NAME=$VARIANT; [ "$SEED" = 0 ] || NAME=${VARIANT}_s$SEED
OUT=$REPO/outputs/${SCENE#"$ROOT"/}/$NAME
mkdir -p "$OUT"
TEST_ITERS=$(python -c "n=$ITER; print(' '.join(str(int(n*f)) for f in (0.25, 0.5, 0.75, 1.0)))")

cd "$REPO"
python train.py --eval -s "$SCENE_DIR" -m "$OUT" -r 1 --gpu -1 --port $((10000 + RANDOM % 20000)) \
  --iterations "$ITER" --appearance_dim 0 --fork 2 --ratio 1 \
  --base_layer 10 --dist2level round --update_ratio 0.2 \
  --progressive --dist_ratio 0.999 --levels -1 --init_level -1 --extra_ratio 0.25 --extra_up 0.01 \
  --test_iterations $TEST_ITERS --save_iterations "$ITER" \
  --seed "$SEED" --visible_threshold 0 --densify_grad_threshold 0.0002 --update_until 25000 \
  "${METHOD[@]}" ${ARGS[@]+"${ARGS[@]}"} 2>&1 | tee "$OUT/train.log"
python eval_bench.py -s "$SCENE_DIR" -m "$OUT" --iteration "$ITER" 2>&1 | tee "$OUT/eval.log"
python metrics_all.py --scene "$SCENE" --data_root "$ROOT" --model_dir "$OUT" ${MASK_ROOT:+--mask_root "$MASK_ROOT"}
