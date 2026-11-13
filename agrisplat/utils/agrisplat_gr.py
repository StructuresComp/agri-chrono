"""GR: Gradient-Ranked Reinvestment of the CP credit, m_t = min(ceil(C_t / K_t), N_t) births per Octree-GS growth round."""
import bisect
import math
import time

import torch

from utils.general_utils import inverse_sigmoid


def unlocked_level(pc, iteration):
    """Finest octree level rendered at this training iteration."""
    if pc.progressive and pc.get_color_mlp.training:
        return min(pc.levels - 1, bisect.bisect_left(pc.coarse_intervals, iteration) + pc.init_level)
    return pc.levels - 1


def integer_level(pred, maximum, mode):
    """GaussianModel.map_to_int_level without side effects."""
    if mode == "floor":
        return pred.floor().long().clamp(0, maximum)
    if mode == "round":
        return pred.round().long().clamp(0, maximum)
    if mode == "ceil":
        return pred.ceil().long().clamp(0, maximum)
    if mode == "progressive":
        return (pred + 1.0).clamp(0.9999, maximum + 0.9999).floor().long()
    raise KeyError(mode)


@torch.no_grad()
def original_admission(pc, positions, levels):
    """Original Octree-GS admission under NF: some training camera selects level L at the cell."""
    admitted = torch.zeros(positions.shape[0], dtype=torch.bool, device=positions.device)
    remaining = torch.arange(positions.shape[0], device=positions.device)
    for camera in pc.cam_infos:
        if remaining.numel() == 0:
            break
        distance = torch.sqrt(torch.sum((positions[remaining] - camera[:3]) ** 2, dim=1)) * camera[3]
        prediction = torch.log2(pc.standard_dist / distance) / math.log2(pc.fork)
        reached = levels[remaining] <= integer_level(prediction, pc.levels - 1, pc.dist2level)
        admitted[remaining[reached]] = True
        remaining = remaining[~reached]
    return admitted


def row_membership(occupied, query):
    """True for each query row present in `occupied`."""
    n = occupied.shape[0]
    if n == 0:
        return torch.zeros(query.shape[0], dtype=torch.bool, device=query.device)
    joined, inverse = torch.unique(torch.cat((occupied, query), dim=0), dim=0, return_inverse=True)
    present = torch.zeros(joined.shape[0], dtype=torch.bool, device=query.device)
    present[inverse[:n]] = True
    return present[inverse[n:]]


def selected_positions(pc, offset_ids):
    """Offset positions x_j = a + o_j s_xyz."""
    anchor_ids = offset_ids // pc.n_offsets
    slot = offset_ids % pc.n_offsets
    return pc.get_anchor[anchor_ids] + pc._offset[anchor_ids, slot] * pc.get_scaling[anchor_ids, :3]


def first_per_group(group, score):
    """Index of the maximum score per group (ties keep input order)."""
    if group.numel() == 0:
        return group.new_empty(0)
    order = torch.argsort(score, descending=True, stable=True)
    order = order[torch.argsort(group[order], stable=True)]
    first = torch.ones(order.numel(), dtype=torch.bool, device=order.device)
    first[1:] = group[order][1:] != group[order][:-1]
    return order[first]


def choose_destinations(cell_id, score, budget):
    """Highest-g offset per cell, then the top-`budget` cells by raw g."""
    eligible = torch.nonzero(score > 0).flatten()
    if eligible.numel() == 0 or budget <= 0:
        return eligible[:0]
    best = eligible[first_per_group(cell_id[eligible], score[eligible])]
    return best[torch.argsort(score[best], descending=True, stable=True)[:budget]]


class AdmissionCache:
    """Exact cell-key -> admission cache (work saving only); reset when the window or active level changes."""

    def __init__(self, capacity=4000000):
        self.capacity = int(capacity)
        self.keys = self.admitted = None
        self.context = None

    def lookup(self, context, keys, compute):
        if context != self.context:
            self.keys = self.admitted = None
            self.context = context
        n = keys.shape[0]
        if self.keys is None:
            slot = torch.full((n,), -1, dtype=torch.long, device=keys.device)
        else:
            m = self.keys.shape[0]
            unique, inverse = torch.unique(torch.cat((self.keys, keys), 0), dim=0, return_inverse=True)
            slots = torch.full((unique.shape[0],), -1, dtype=torch.long, device=keys.device)
            slots[inverse[:m]] = torch.arange(m, device=keys.device)
            slot = slots[inverse[m:]]
        hit = slot >= 0
        missing = torch.nonzero(~hit).flatten()
        admitted = torch.zeros(n, dtype=torch.bool, device=keys.device)
        if self.keys is not None:
            admitted[hit] = self.admitted[slot[hit]]
        if missing.numel():
            admitted[missing] = compute(missing)
        old_n = 0 if self.keys is None else self.keys.shape[0]
        if old_n + missing.numel() <= self.capacity:
            if self.keys is None:
                self.keys, self.admitted = keys[missing].clone(), admitted[missing].clone()
            elif missing.numel():
                self.keys = torch.cat((self.keys, keys[missing]), 0)
                self.admitted = torch.cat((self.admitted, admitted[missing]), 0)
        else:
            self.keys, self.admitted = keys[:self.capacity].clone(), admitted[:self.capacity].clone()
        return admitted


@torch.no_grad()
def append_anchors(pc, positions, levels, features):
    """Append anchors with the Octree-GS birth initialisation and the given (parent) features."""
    n = positions.shape[0]
    dev = pc._anchor.device
    size = (pc.voxel_size / (float(pc.fork) ** levels.float())).view(-1, 1)          # q_L
    new_rotation = torch.zeros([n, 4], dtype=torch.float, device=dev)
    new_rotation[:, 0] = 1.0
    d = {"anchor": positions.float(),
         "scaling": torch.log(torch.ones([n, 6], dtype=torch.float, device=dev) * size),
         "rotation": new_rotation,
         "anchor_feat": features,
         "offset": torch.zeros([n, pc.n_offsets, 3], dtype=torch.float, device=dev),
         "opacity": inverse_sigmoid(0.1 * torch.ones((n, 1), dtype=torch.float, device=dev))}
    pc.anchor_demon = torch.cat([pc.anchor_demon, torch.zeros([n, 1], device=dev).float()], dim=0)
    pc.opacity_accum = torch.cat([pc.opacity_accum, torch.zeros([n, 1], device=dev).float()], dim=0)
    optimizable_tensors = pc.cat_tensors_to_optimizer(d)
    pc._anchor = optimizable_tensors["anchor"]
    pc._scaling = optimizable_tensors["scaling"]
    pc._rotation = optimizable_tensors["rotation"]
    pc._anchor_feat = optimizable_tensors["anchor_feat"]
    pc._offset = optimizable_tensors["offset"]
    pc._opacity = optimizable_tensors["opacity"]
    pc._level = torch.cat([pc._level, levels.view(-1, 1).float()], dim=0)
    pc._extra_level = torch.cat([pc._extra_level, torch.zeros(n, dtype=torch.float, device=dev)], dim=0)


def candidate_offsets(pc, iteration, grads, offset_mask, n_before, grad_threshold, update_ratio):
    """Eligible offsets: n_j > n_min (offset_mask), 0 < g_j < tau_L(j), active level."""
    offset_lv = pc.get_level[:n_before].view(-1).long().repeat_interleave(pc.n_offsets)
    tau_L = grad_threshold * (pc.fork ** update_ratio) ** offset_lv.float()
    j = torch.nonzero(offset_mask & (grads > 0) & (grads < tau_L)).flatten()
    return j[offset_lv[j] <= unlocked_level(pc, iteration)], offset_lv


def destination_cells(pc, j, L_j):
    """Same-level destination cells of the offsets j and their corner positions."""
    q_j = pc.voxel_size / (float(pc.fork) ** L_j.float())
    grid = torch.round((selected_positions(pc, j) - pc.init_pos) / q_j[:, None]).long()
    cells, cell_of_j = torch.unique(torch.cat((L_j[:, None], grid), dim=1), dim=0, return_inverse=True)
    cell_lv = cells[:, 0]
    cell_x = cells[:, 1:] * (pc.voxel_size / (float(pc.fork) ** cell_lv.float()))[:, None] + pc.init_pos
    return cells, cell_of_j, cell_lv, cell_x


def unoccupied(pc, cells, cell_lv):
    """True for cells holding no anchor of their level."""
    free = torch.zeros(cells.shape[0], dtype=torch.bool, device=cells.device)
    for level in torch.unique(cell_lv).tolist():
        rows = torch.nonzero(cell_lv == level).flatten()
        occupied_x = pc.get_anchor[pc.get_level.view(-1) == level]
        if occupied_x.shape[0]:
            occupied_grid = torch.round((occupied_x - pc.init_pos) / (pc.voxel_size / pc.fork ** level)).long()
            rows = rows[~row_membership(occupied_grid, cells[rows, 1:])]
        free[rows] = True
    return free


class GradientReinvestment:
    """GR round, called by GaussianModel.adjust_anchor after the Octree-GS growth; spends the credit of `cp`."""

    def __init__(self, cp, logger):
        self.cp, self.logger = cp, logger
        self.cache = AdmissionCache()

    @torch.no_grad()
    def __call__(self, pc, iteration, grads, offset_mask, n_before, grad_threshold, update_ratio):
        cp = self.cp
        if cp.credit <= 0 or iteration >= cp.until:
            return
        if pc.visible_threshold != 0:
            raise ValueError('GR admission is the NF rule (visible_threshold 0, original_admission): use --visible_threshold 0')
        started = time.perf_counter()
        n_now = pc.get_anchor.shape[0]
        K_t = max(1, (cp.window_end - iteration) // cp.growth_interval + 1)      # growth rounds left in the window
        budget = (cp.credit + K_t - 1) // K_t                                   # ceil(C_t / K_t)
        rec = dict(iteration=int(iteration), credit_before=int(cp.credit), K_t=int(K_t), budget=int(budget))
        j, offset_lv = candidate_offsets(pc, iteration, grads, offset_mask, n_before, grad_threshold, update_ratio)
        rec['candidate_offsets'] = int(j.numel())
        m_t = 0
        if j.numel():
            cells, cell_of_j, cell_lv, cell_x = destination_cells(pc, j, offset_lv[j])
            in_A = unoccupied(pc, cells, cell_lv)
            free_rows = torch.nonzero(in_A).flatten()
            if free_rows.numel():
                in_A[free_rows] = self.cache.lookup(
                    (cp.window_end, unlocked_level(pc, iteration)), cells[free_rows],
                    lambda m: original_admission(pc, cell_x[free_rows][m], cell_lv[free_rows][m]))
            s_j = torch.where(in_A[cell_of_j], grads[j].double(), torch.zeros_like(grads[j], dtype=torch.float64))
            chosen = choose_destinations(cell_of_j, s_j, budget)                 # m_t = min(budget, N_t)
            m_t = int(chosen.numel())
            if m_t:
                parent = j[chosen] // pc.n_offsets
                append_anchors(pc, cell_x[cell_of_j[chosen]], cell_lv[cell_of_j[chosen]], pc._anchor_feat[parent].detach().clone())
            rec.update(candidate_cells=int(cells.shape[0]), cells_in_A=int(in_A.sum()))
        cp.credit -= m_t
        cp.reinvested += m_t
        rec.update(m_t=m_t, credit_after=int(cp.credit), N_before=int(n_now), N_after=int(pc.get_anchor.shape[0]),
                   t_s=time.perf_counter() - started)
        self.logger.info(f'[AgriSplat GR] {rec}')
