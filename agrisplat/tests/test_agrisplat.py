"""CPU tests of NF, CP, GR, ADS and the options."""
import ast
import math
import sys
from argparse import ArgumentParser
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

TREE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TREE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cpu_model import ListLogger, assert_same_state, load_model_class, make_model, model_state
from arguments import AgriSplatParams, ModelParams, OptimizationParams, PipelineParams
import utils.agrisplat_cp as agrisplat_cp
from utils.agrisplat_gr import GradientReinvestment, unlocked_level
from utils.agrisplat_cp import ContributionPruning
from utils.loss_utils import ads_loss

GaussianModel = load_model_class()
DEFAULTS = dict(cp=1, cp_threshold=8.0, cp_interval=5000, cp_until=25000, gr=1, gr_credit_fraction=1.0, ads=1,
                ads_start=25000, ads_weight=1.0)


def options(**kw):
    return SimpleNamespace(**{**DEFAULTS, **kw})


def growth_inputs(pc):
    grads = pc.offset_gradient_accum / pc.offset_denom
    grads[grads.isnan()] = 0.0
    return torch.norm(grads, dim=-1), (pc.offset_denom > 100 * 0.8 * 0.5).squeeze(dim=1)


def test_option_defaults_are_the_published_constants():
    p = ArgumentParser()
    ap = AgriSplatParams(p)
    assert vars(ap.extract(p.parse_args([]))) == DEFAULTS


def test_options_override():
    p = ArgumentParser()
    ap = AgriSplatParams(p)
    a = ap.extract(p.parse_args("--cp 0 --cp_threshold 4 --cp_interval 2500 --cp_until 15000 --gr 0 --gr_credit_fraction 0.5 "
                                "--ads 0 --ads_start 5000 --ads_weight 0.25".split()))
    assert vars(a) == dict(cp=0, cp_threshold=4.0, cp_interval=2500, cp_until=15000, gr=0, gr_credit_fraction=0.5, ads=0,
                           ads_start=5000, ads_weight=0.25)


def test_nf_is_the_default_visibility_setting():
    p = ArgumentParser()
    lp = ModelParams(p)
    assert lp.extract(p.parse_args(["-s", "x"])).visible_threshold == 0.0


def test_training_parser_has_one_definition_per_option():
    p = ArgumentParser()
    for group in (ModelParams, OptimizationParams, PipelineParams, AgriSplatParams):
        group(p)
    p.parse_args([])


def test_invalid_cp_settings_are_rejected():
    with pytest.raises(ValueError):
        ContributionPruning(options(cp_until=30000), 25000, 100)
    with pytest.raises(ValueError):
        ContributionPruning(options(gr_credit_fraction=-1.0), 25000, 100)
    with pytest.raises(ValueError):
        ContributionPruning(options(cp_interval=0), 25000, 100)


def ads_reference(render, gt):
    """L_ADS by explicit loops."""
    w = torch.tensor([0.299, 0.587, 0.114], dtype=render.dtype)
    Y, G = (render * w[:, None, None]).sum(0), (gt * w[:, None, None]).sum(0)
    H, W = Y.shape
    total = 0.0
    for y in range(H - 1):
        for x in range(W - 1):
            g = (Y[y, x + 1] - Y[y, x], Y[y + 1, x] - Y[y, x])
            h = (G[y, x + 1] - G[y, x], G[y + 1, x] - G[y, x])
            n = math.hypot(float(h[0]), float(h[1]))
            total += 0.0 if n == 0 else max(0.0, n - float(g[0] * h[0] + g[1] * h[1]) / n)
    return total / ((H - 1) * (W - 1))


def test_ads_loss_equals_the_closed_form():
    g = torch.Generator().manual_seed(1)
    render, gt = torch.rand(3, 9, 11, generator=g, dtype=torch.float64), torch.rand(3, 9, 11, generator=g, dtype=torch.float64)
    assert math.isclose(float(ads_loss(render, gt)), ads_reference(render, gt), rel_tol=1e-12)


def test_ads_loss_penalises_only_missing_contrast_along_the_gt_edge():
    gt = torch.zeros(3, 4, 4, dtype=torch.float64)
    gt[:, :, 2:] = 1.0
    assert ads_loss(gt.clone(), gt) == 0
    sharper = gt.clone(); sharper[:, :, 2:] = 2.0
    assert ads_loss(sharper, gt) == 0                    # excess contrast is not penalised
    flat = torch.full_like(gt, 0.5)
    assert math.isclose(float(ads_loss(flat, gt)), 3 / 9)


def test_ads_loss_is_zero_where_the_gt_gradient_vanishes():
    gt = torch.full((3, 6, 7), 0.3, dtype=torch.float64)
    render = torch.rand(3, 6, 7, dtype=torch.float64, generator=torch.Generator().manual_seed(2)).requires_grad_()
    loss = ads_loss(render, gt)
    loss.backward()
    assert loss == 0 and torch.count_nonzero(render.grad) == 0


def test_ads_loss_does_not_backpropagate_into_the_gt():
    gt = torch.rand(3, 5, 5, requires_grad=True)
    render = torch.rand(3, 5, 5, requires_grad=True)
    ads_loss(render, gt).backward()
    assert gt.grad is None and render.grad is not None


def ads_gate():
    tree = ast.parse((TREE / "train.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and "ads_loss" in ast.unparse(node.body[0]):
            return node
    raise AssertionError("ADS hook not found in train.py")


@pytest.mark.parametrize("ads_start", [1, 5000, 15000, 25000])
def test_ads_is_active_from_ads_start(ads_start):
    test = compile(ast.Expression(ads_gate().test), "gate", "eval")
    for t in (1, ads_start - 1, ads_start, ads_start + 1, 40000):
        assert eval(test, dict(ap=options(ads=1, ads_start=ads_start), iteration=t)) == (t >= ads_start)
        assert not eval(test, dict(ap=options(ads=0, ads_start=ads_start), iteration=t))


def test_ads_is_weighted_by_ads_weight():
    body = [ast.unparse(s) for s in ads_gate().body]
    assert "loss = loss + ap.ads_weight * L_ADS" in body


def run_cp(pc, W, iteration, **kw):
    cp = ContributionPruning(options(**kw), 25000, 100)
    saved = agrisplat_cp.anchor_contribution
    agrisplat_cp.anchor_contribution = lambda *a, **k: W.clone()
    try:
        with torch.no_grad():
            rec = cp.prune_round(pc, [], None, iteration, ListLogger())
    finally:
        agrisplat_cp.anchor_contribution = saved
    return cp, rec


def contributions(pc, seed=3):
    return torch.rand(pc.get_anchor.shape[0], generator=torch.Generator().manual_seed(seed), dtype=torch.float64) * 16.0


@pytest.mark.parametrize("theta", [8.0, 4.0])
@pytest.mark.parametrize("iteration", [5000, 10000])
def test_cp_removes_active_anchors_below_threshold(theta, iteration):
    pc = make_model(GaussianModel)
    W = contributions(pc)
    level = pc.get_level.view(-1).long()
    unlock = torch.tensor([0.0, 0.0] + list(pc.coarse_intervals), dtype=torch.float64)
    expected_removed = (unlock[level] <= iteration) & (W < theta)
    kept_before = model_state(pc)
    cp, rec = run_cp(pc, W, iteration, cp_threshold=theta)
    keep = ~expected_removed
    assert rec["removed"] == int(expected_removed.sum()) > 0
    assert torch.equal(pc.get_anchor, kept_before["_anchor"][keep])
    assert torch.equal(pc.anchor_demon, kept_before["anchor_demon"][keep])
    assert torch.equal(pc.offset_denom, kept_before["offset_denom"][keep.repeat_interleave(pc.n_offsets)])
    if iteration == 5000:   # inactive levels are never judged
        assert bool(((level >= 2) & (W < theta)).any())
    assert cp.credit == rec["removed"]


def test_cp_threshold_changes_the_selection():
    W = contributions(make_model(GaussianModel))
    assert run_cp(make_model(GaussianModel), W, 10000, cp_threshold=4.0)[1]["removed"] < \
        run_cp(make_model(GaussianModel), W, 10000, cp_threshold=8.0)[1]["removed"]


@pytest.mark.parametrize("interval,until,rounds", [
    (5000, 25000, [5000, 10000, 15000, 20000, 25000]),
    (2500, 25000, list(range(2500, 25001, 2500))),
    (10000, 25000, [10000, 20000]),
    (5000, 15000, [5000, 10000, 15000]),
])
def test_cp_rounds_and_credit_windows(interval, until, rounds):
    r = ContributionPruning(options(cp_interval=interval, cp_until=until), 25000, 100)
    assert [t for t in range(1, 40001) if r.is_round(t)] == rounds
    for t in rounds:
        r.add_credit(10, t)
        if t < until:
            assert r.window_end == min(t + interval, until - 1)
    credited = [t for t in rounds if t < until]
    assert r.credit == 10 * len(credited) and r.lost_credit == 10 * (len(rounds) - len(credited))


@pytest.mark.parametrize("eta,removed,credit", [(1.0, 7, 7), (0.5, 7, 3), (2.0, 7, 14), (0.25, 3, 0), (0.0, 9, 0)])
def test_credit_is_floor_of_fraction_times_removed(eta, removed, credit):
    r = ContributionPruning(options(gr_credit_fraction=eta), 25000, 100)
    r.add_credit(removed, 5000)
    assert r.credit == credit


def gr_reference(pc, iteration, grads, offset_mask, budget):
    """Brute-force GR births [(corner, level, parent feature)] in birth order."""
    K = pc.n_offsets
    active = unlocked_level(pc, iteration)
    best = {}
    for j in range(grads.numel()):
        a, L = j // K, int(pc.get_level[j // K])
        tau = 0.0002 * (2 ** 0.2) ** L
        g = float(grads[j])
        if not (bool(offset_mask[j]) and 0 < g < tau and L <= active):
            continue
        q = 1.0 / 2 ** L
        x = pc.get_anchor[a] + pc._offset[a, j % K] * pc.get_scaling[a, :3]
        cell = (L,) + tuple(int(v) for v in torch.round(x / q).long())
        occupied = any(int(pc.get_level[b]) == L and tuple(int(v) for v in torch.round(pc.get_anchor[b] / q).long()) == cell[1:]
                       for b in range(pc.get_anchor.shape[0]))
        corner = torch.tensor(cell[1:], dtype=torch.float32) * q
        admitted = any(L <= min(max(round(math.log2(4.0 / (float(torch.linalg.norm(corner - c[:3])) * float(c[3])))), 0), 3)
                       for c in pc.cam_infos)
        if occupied or not admitted:
            continue
        if cell not in best or g > best[cell][0]:
            best[cell] = (g, j)
    ranked = sorted(best.items(), key=lambda kv: -kv[1][0])[:budget]
    return [(torch.tensor(c[1:], dtype=torch.float32) / 2 ** c[0], c[0], pc._anchor_feat[j // K].detach()) for c, (g, j) in ranked]


@pytest.mark.parametrize("iteration", [5100, 8100, 12100])
def test_gr_births_follow_the_brute_force_rule(iteration):
    pc = make_model(GaussianModel)
    grads, offset_mask = growth_inputs(pc)
    r = ContributionPruning(options(), 25000, 100)
    r.credit, r.window_end = 60, iteration + 400
    expected = gr_reference(pc, iteration, grads, offset_mask, 12)
    n0 = pc.get_anchor.shape[0]
    log = ListLogger()
    GradientReinvestment(r, log)(pc, iteration, grads, offset_mask, n0, 0.0002, 0.2)
    rec = ast.literal_eval(log.lines[-1].split("] ", 1)[1])
    assert (rec["K_t"], rec["budget"]) == (5, 12)
    assert rec["m_t"] == len(expected) > 0 and r.credit == 60 - len(expected)
    for i, (x, L, feat) in enumerate(expected):
        assert torch.allclose(pc.get_anchor[n0 + i], x) and int(pc.get_level[n0 + i]) == L
        assert torch.equal(pc._anchor_feat[n0 + i], feat)
        assert torch.equal(pc._offset[n0 + i], torch.zeros(pc.n_offsets, 3))
        assert torch.allclose(pc.get_scaling[n0 + i], torch.full((6,), 1.0 / 2 ** L))
    assert pc.anchor_demon.shape[0] == pc.opacity_accum.shape[0] == pc.get_anchor.shape[0]


def test_gr_fixture_exercises_every_rejection():
    pc = make_model(GaussianModel)
    grads, offset_mask = growth_inputs(pc)
    everything = gr_reference(pc, 12100, grads, offset_mask, 10 ** 6)
    early = gr_reference(pc, 5100, grads, offset_mask, 10 ** 6)
    assert len(everything) > 12 and len(early) < len(everything)
    assert any(L >= 2 for _, L, _ in everything) and all(L <= 1 for _, L, _ in early)


@pytest.mark.parametrize("interval,t_round,t,K_t", [(5000, 5000, 5100, 50), (2500, 5000, 5100, 25), (10000, 10000, 10100, 100),
                                                     (10000, 20000, 20100, 49), (5000, 20000, 24900, 1)])
def test_gr_budget_spreads_the_credit_over_the_window(interval, t_round, t, K_t):
    pc = make_model(GaussianModel)
    grads, offset_mask = growth_inputs(pc)
    r = ContributionPruning(options(cp_interval=interval), 25000, 100)
    r.add_credit(101, t_round)
    log = ListLogger()
    GradientReinvestment(r, log)(pc, t, grads, offset_mask, pc.get_anchor.shape[0], 0.0002, 0.2)
    rec = ast.literal_eval(log.lines[-1].split("] ", 1)[1])
    assert (rec["K_t"], rec["budget"]) == (K_t, -(-101 // K_t))


@pytest.mark.parametrize("credit,iteration", [(0, 8100), (50, 15000)])
def test_gr_is_inert_without_credit_or_after_cp_until(credit, iteration):
    pc = make_model(GaussianModel)
    grads, offset_mask = growth_inputs(pc)
    r = ContributionPruning(options(cp_until=15000), 25000, 100)
    r.credit, r.window_end = credit, 14999
    before = model_state(pc)
    log = ListLogger()
    GradientReinvestment(r, log)(pc, iteration, grads, offset_mask, pc.get_anchor.shape[0], 0.0002, 0.2)
    assert log.lines == [] and r.credit == credit
    assert_same_state(before, model_state(pc))


def test_gr_requires_visible_threshold_zero():
    pc = make_model(GaussianModel)
    pc.visible_threshold = 0.1
    grads, offset_mask = growth_inputs(pc)
    r = ContributionPruning(options(), 25000, 100)
    r.credit, r.window_end = 10, 9999
    with pytest.raises(ValueError):
        GradientReinvestment(r, ListLogger())(pc, 8100, grads, offset_mask, pc.get_anchor.shape[0], 0.0002, 0.2)


def test_adjust_anchor_with_inert_gr_equals_octree_gs_growth():
    kw = dict(iteration=8100, check_interval=100, success_threshold=0.8, grad_threshold=0.0002, update_ratio=0.2,
              extra_ratio=0.25, extra_up=0.01, min_opacity=0.005)
    a, b = make_model(GaussianModel), make_model(GaussianModel)
    with torch.no_grad():
        a.adjust_anchor(**kw)
        b.adjust_anchor(**kw, reinvest=GradientReinvestment(ContributionPruning(options(), 25000, 100), ListLogger()))
    assert_same_state(model_state(a), model_state(b))


def module_setup(**kw):
    """Run the CP / GR construction block of train.py."""
    src = (TREE / "train.py").read_text()
    start = src.index("    if ap.gr and not ap.cp:")
    block = src[start:src.index("    logger.info(f'[AgriSplat] options", start)]
    env = dict(ap=options(**kw), opt=SimpleNamespace(update_until=25000, update_interval=100), logger=ListLogger(),
               ContributionPruning=ContributionPruning, GradientReinvestment=GradientReinvestment)
    exec(compile("\n".join(line[4:] for line in block.splitlines()), "train.py", "exec"), env)
    return env["cp"], env["gr"]


@pytest.mark.parametrize("cp,gr", [(0, 0), (1, 0), (1, 1)])
def test_module_switches_build_only_their_modules(cp, gr):
    built_cp, built_gr = module_setup(cp=cp, gr=gr)
    assert (built_cp is not None) == bool(cp) and (built_gr is not None) == bool(gr)
    if gr:
        assert built_gr.cp is built_cp


def test_gr_requires_cp():
    with pytest.raises(ValueError):
        module_setup(cp=0, gr=1)


def test_module_hooks_are_guarded():
    src = (TREE / "train.py").read_text()
    assert "if cp is not None and cp.is_round(iteration):" in src and "reinvest=gr," in src
    gm = (TREE / "scene/gaussian_model.py").read_text()
    assert gm.count("reinvest(") == 1 and "if reinvest is not None:" in gm


def test_scene_names_resolve_under_the_data_root(tmp_path, monkeypatch):
    (tmp_path / "Table2/Week3").mkdir(parents=True)
    p = ArgumentParser()
    lp = ModelParams(p)
    monkeypatch.setenv("AGRISPLAT_DATA", "/nonexistent")
    assert lp.extract(p.parse_args(["-s", "Table2/Week3", "--data_root", str(tmp_path)])).source_path == str(tmp_path / "Table2/Week3")
    monkeypatch.setenv("AGRISPLAT_DATA", str(tmp_path))
    assert lp.extract(p.parse_args(["-s", "Table2/Week3"])).source_path == str(tmp_path / "Table2/Week3")
    monkeypatch.delenv("AGRISPLAT_DATA")
    assert lp.extract(p.parse_args(["-s", "Table2/Week3"])).source_path == str(TREE / "datasets/Table2/Week3")


def test_instrumentation_is_outside_the_optimisation_path():
    """timing / VRAM variables are only assigned and reported; they never enter the model, loss or optimizer"""
    names = {"_vram", "_t_loop", "_t_report", "_t", "_t_start_wall", "_eff"}
    tree = ast.parse((TREE / "train.py").read_text())
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.stmt) and not isinstance(stmt, (ast.FunctionDef, ast.For, ast.If, ast.With, ast.While)):
            used = {n.id for n in ast.walk(stmt) if isinstance(n, ast.Name)}
            if used & names:
                text = ast.unparse(stmt)
                assert not any(w in text for w in ("gaussians.optimizer", "loss", "backward", "adjust_anchor", "prune")), text


def test_peak_vram_without_nvml_is_none(monkeypatch):
    import importlib.util
    from utils.vram_monitor import PeakVRAM
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    assert PeakVRAM().stop() is None


def test_region_metrics_edge_and_energy_definitions():
    import metrics_all
    g = torch.rand(40, 50, 3, generator=torch.Generator().manual_seed(0)).numpy()
    roi = g[:, :, 0] >= 0
    er, erm, eg, egm = metrics_all.edge_counts(g, g, roi)
    assert er == erm == eg == egm > 0                           # identical images: every edge matched
    assert abs(metrics_all.sobel_energy(g * 0.5).sum() / metrics_all.sobel_energy(g).sum() - 0.25) < 1e-6
    assert metrics_all.edge_counts(g, g, ~roi).sum() == 0       # region-restricted
