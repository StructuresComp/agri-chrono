"""CP: Contribution Pruning, W_a = sum_v sum_{i in a} sum_p alpha_ip T_ip; anchors with W_a < theta_W are removed."""
import math
import time

import torch
from diff_gaussian_rasterization import GaussianRasterizationSettings, GaussianRasterizer
from gaussian_renderer import prefilter_voxel, generate_neural_gaussians


def _rasterize(view, xyz, color, opacity, scaling, rot, bg):
    rs = GaussianRasterizationSettings(image_height=int(view.image_height), image_width=int(view.image_width),
                                       tanfovx=math.tan(view.FoVx * 0.5), tanfovy=math.tan(view.FoVy * 0.5), bg=bg, scale_modifier=1.0,
                                       viewmatrix=view.world_view_transform, projmatrix=view.full_proj_transform, sh_degree=1,
                                       campos=view.camera_center, prefiltered=False, debug=False)
    means2D = torch.zeros_like(xyz, requires_grad=True)
    img, _ = GaussianRasterizer(raster_settings=rs)(means3D=xyz, means2D=means2D, shs=None, colors_precomp=color, opacities=opacity,
                                                    scales=scaling, rotations=rot, cov3D_precomp=None)
    return img


def anchor_contribution(pc, views, pipe, iteration):
    """W_a (float64) over the training views, with the training LoD mask."""
    bg = torch.zeros(3, device='cuda')
    W = torch.zeros(pc.get_anchor.shape[0], device='cuda', dtype=torch.float64)
    saved = pc._anchor_mask
    for v in views:
        with torch.no_grad():
            pc.set_anchor_mask(v.camera_center, iteration, v.resolution_scale)
            vis = prefilter_voxel(v, pc, pipe, bg)
            xyz, color, opacity, scaling, rot, _, mask = generate_neural_gaussians(v, pc, vis, is_training=True)
            aidx = torch.nonzero(vis).squeeze(1).repeat_interleave(pc.n_offsets)[mask]
        if xyz.shape[0] == 0:
            continue
        with torch.enable_grad():
            c = color.detach().clone().requires_grad_(True)
            img = _rasterize(v, xyz.detach(), c, opacity.detach(), scaling.detach(), rot.detach(), bg)
            img[0].sum().backward()                                  # d(sum_p R_p) / d c_i,R = sum_p alpha_ip T_ip
        W.index_add_(0, aidx, c.grad[:, 0].double())
    pc._anchor_mask = saved
    return W


def level_unlock_iter(pc):
    """First training iteration at which each octree level is rendered (progressive schedule)."""
    unlock = torch.zeros(pc.levels, dtype=torch.float64)
    if pc.progressive:
        for L in range(pc.init_level + 1, pc.levels):
            unlock[L] = float(pc.coarse_intervals[L - pc.init_level - 1])
    return unlock


def cp_eligible(pc, iteration):
    """Anchors of active levels (inactive levels are not rendered, so their W_a = 0 says nothing)."""
    unlock_a = level_unlock_iter(pc).to(pc.get_anchor.device)[pc.get_level.view(-1).long()]
    return unlock_a <= iteration


class ContributionPruning:
    """CP rounds every Delta_CP up to T_CP; the removed count accumulates as reinvestment credit C for GR."""

    def __init__(self, ap, update_until, growth_interval):
        if ap.cp_until > update_until:
            raise ValueError(f'--cp_until {ap.cp_until} > --update_until {update_until}: GR runs inside the Octree-GS growth rounds')
        if ap.cp_interval <= 0 or ap.gr_credit_fraction < 0:
            raise ValueError(f'--cp_interval {ap.cp_interval} must be > 0 and --gr_credit_fraction {ap.gr_credit_fraction} >= 0')
        self.theta_W = float(ap.cp_threshold)
        self.interval = int(ap.cp_interval)             # Delta_CP
        self.until = int(ap.cp_until)                   # T_CP
        self.eta = float(ap.gr_credit_fraction)
        self.growth_interval = int(growth_interval)
        self.credit = 0                                 # C
        self.window_end = 0
        self.reinvested = 0
        self.lost_credit = 0

    def is_round(self, iteration):
        return iteration % self.interval == 0 and iteration <= self.until

    def add_credit(self, n_removed, iteration):
        """C += floor(eta n_removed) and open the window up to min(t + Delta_CP, T_CP - 1); removals at T_CP are not credited."""
        if iteration < self.until:
            self.credit += math.floor(self.eta * int(n_removed))
            self.window_end = min(iteration + self.interval, self.until - 1)
        else:
            self.lost_credit += int(n_removed)

    def prune_round(self, pc, views, pipe, iteration, logger):
        t0 = time.time()
        W = anchor_contribution(pc, views, pipe, iteration)
        eligible = cp_eligible(pc, iteration)
        removed = eligible & (W < self.theta_W)
        level = pc.get_level.view(-1)
        rec = dict(iteration=int(iteration), N_before=int(W.numel()), eligible=int(eligible.sum()), removed=int(removed.sum()),
                   removed_per_level={int(L): int((removed & (level == L)).sum()) for L in torch.unique(level).tolist()},
                   W_median=float(W.median()), credit_before=int(self.credit))
        if removed.any():
            keep = ~removed
            if hasattr(pc, 'opacity_accum'):              # growth statistics exist until update_until
                pc.opacity_accum = pc.opacity_accum[keep]
                pc.anchor_demon = pc.anchor_demon[keep]
                keep_offsets = keep.repeat_interleave(pc.n_offsets)
                pc.offset_gradient_accum = pc.offset_gradient_accum[keep_offsets]
                pc.offset_denom = pc.offset_denom[keep_offsets]
            pc.prune_anchor(removed)
        self.add_credit(rec['removed'], iteration)
        torch.cuda.empty_cache()
        rec.update(N_after=int(pc.get_anchor.shape[0]), credit_after=int(self.credit), reinvested_so_far=int(self.reinvested),
                   lost_credit=int(self.lost_credit), t_s=time.time() - t0)
        logger.info(f'[AgriSplat CP] {rec}')
        return rec
