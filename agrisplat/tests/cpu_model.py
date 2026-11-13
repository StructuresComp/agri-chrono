"""CPU fixture: the real GaussianModel compiled with CUDA placements mapped to the CPU, and a small anchor octree."""
import types
from pathlib import Path

import torch

TREE = Path(__file__).resolve().parents[1]


def cpu_source(path, extra=()):
    src = Path(path).read_text()
    for old, new in tuple(extra) + ((".cuda()", ""), ('device="cuda"', 'device="cpu"'), ("device='cuda'", "device='cpu'"),
                                    (".to('cuda')", "")):
        src = src.replace(old, new)
    return src


def load_model_class(tree=TREE, extra=()):
    path = Path(tree) / "scene/gaussian_model.py"
    module = types.ModuleType(f"cpu_gaussian_model_{Path(tree).name}")
    module.__file__ = str(path)
    exec(compile(cpu_source(path, extra), str(path), "exec"), module.__dict__)
    return module.GaussianModel


def make_model(GaussianModel, seed=0, n_anchors=48, n_offsets=4, levels=4):
    torch.manual_seed(0)
    pc = GaussianModel(feat_dim=4, n_offsets=n_offsets, fork=2, use_feat_bank=False, appearance_dim=0, visible_threshold=0.0,
                       dist2level="round", base_layer=10, progressive=True, extend=1.1)
    g = torch.Generator().manual_seed(seed)
    pc.levels, pc.init_level = levels, 1
    pc.voxel_size, pc.init_pos, pc.standard_dist = torch.tensor(1.0), torch.zeros(3), torch.tensor(4.0)
    pc.set_coarse_interval(10000, 1.5)
    pc.cam_infos = torch.tensor([[0.5, 0.5, 0.5, 1.0], [3.0, 3.0, 1.0, 1.0], [5.0, 1.0, 2.0, 1.0]])
    level = torch.randint(0, levels, (n_anchors,), generator=g)
    size = 1.0 / 2 ** level.float()
    pos = torch.floor(torch.rand(n_anchors, 3, generator=g) * 6.0 / size[:, None]) * size[:, None]
    params = dict(anchor=pos, offset=torch.randn(n_anchors, n_offsets, 3, generator=g) * 0.7,
                  anchor_feat=torch.randn(n_anchors, 4, generator=g), opacity=torch.zeros(n_anchors, 1),
                  scaling=torch.log(size)[:, None].repeat(1, 6), rotation=torch.tensor([[1.0, 0, 0, 0]]).repeat(n_anchors, 1))
    for name, value in params.items():
        setattr(pc, "_" + name, torch.nn.Parameter(value.clone()))
    pc._level = level.int().unsqueeze(1)
    pc._extra_level = torch.zeros(n_anchors)
    pc._anchor_mask = torch.ones(n_anchors, dtype=torch.bool)
    pc.offset_denom = torch.randint(0, 100, (n_anchors * n_offsets, 1), generator=g).float()
    pc.offset_gradient_accum = torch.rand(n_anchors * n_offsets, 1, generator=g) * 0.0006 * pc.offset_denom
    pc.anchor_demon = torch.randint(0, 120, (n_anchors, 1), generator=g).float()
    pc.opacity_accum = torch.rand(n_anchors, 1, generator=g) * 0.01 * pc.anchor_demon
    pc.optimizer = torch.optim.Adam([dict(params=[getattr(pc, "_" + n)], name=n, lr=0.001) for n in params], lr=0.0, eps=1e-15)
    for n in params:
        getattr(pc, "_" + n).grad = torch.randn(getattr(pc, "_" + n).shape, generator=g)
    pc.optimizer.step()
    pc.optimizer.zero_grad(set_to_none=True)
    return pc


def model_state(pc):
    state = {n: getattr(pc, n).detach().clone() for n in ("_anchor", "_offset", "_anchor_feat", "_opacity", "_scaling",
                                                         "_rotation", "_level", "_extra_level", "anchor_demon")}
    for n in ("opacity_accum", "offset_gradient_accum", "offset_denom"):
        if hasattr(pc, n):
            state[n] = getattr(pc, n).clone()
    for group in pc.optimizer.param_groups:
        st = pc.optimizer.state[group["params"][0]]
        state["adam_" + group["name"]] = (st["exp_avg"].clone(), st["exp_avg_sq"].clone())
    return state


def assert_same_state(a, b):
    assert a.keys() == b.keys()
    for k in a:
        x, y = (a[k], b[k]) if k.startswith("adam_") else ((a[k],), (b[k],))
        for u, v in zip(x, y):
            assert u.dtype == v.dtype and torch.equal(u, v), k


class ListLogger:
    def __init__(self):
        self.lines = []

    def info(self, msg):
        self.lines.append(msg)
