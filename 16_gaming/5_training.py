"""
PyTorch training integration with Chalk datasets.

Four patterns for feeding Chalk features into a training loop:

  1. Offline batch     — offline_query → get_data_as_dataframe() → chalkdf
  2a. Streaming        — create_torch_iter_dataset() + DataLoader
  2b. Staged download  — download_data() + create_torch_map_dataset()
  3. DDP multi-GPU     — staged download + DistributedSampler

All patterns query the same feature contract. Transformations are pushed
upstream into Chalk resolvers (4_preprocessing.py), so the collate_fn
only splits the dict — no local scaling, encoding, or DataFrame round-trip.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import torch
import torch.distributed as dist
from chalk.client import ChalkClient
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

from features import PlayerFeatures

OUTPUT_FEATURES = [
    PlayerFeatures.engagement_scaled,
    PlayerFeatures.session_length_scaled,
    PlayerFeatures.win_rate_scaled,
    PlayerFeatures.player_tier_encoded,
    PlayerFeatures.region_encoded,
    PlayerFeatures.target,
]

_PREFIX = "player_features."
_FEATURE_COLS = [
    f"{_PREFIX}engagement_scaled",
    f"{_PREFIX}session_length_scaled",
    f"{_PREFIX}win_rate_scaled",
    f"{_PREFIX}player_tier_encoded",
    f"{_PREFIX}region_encoded",
]
_TARGET_COL = f"{_PREFIX}target"


# ---------------------------------------------------------------------------
# Shared collate_fn
# ---------------------------------------------------------------------------

def make_collate(
    feature_cols: list[str],
    target_col: str,
    prepare_targets: Callable[[torch.Tensor], torch.Tensor] | None = None,
) -> Callable:
    """Build a collate_fn that maps a Chalk batch dict to an (x, y) tuple."""
    _prepare = prepare_targets or (lambda t: t)

    def _to_tensor(v) -> torch.Tensor:
        if isinstance(v, torch.Tensor):
            return v
        return torch.tensor(0.0 if v is None else v)

    _needed = set(feature_cols) | {target_col}

    def collate(batch) -> tuple[torch.Tensor, torch.Tensor]:
        if isinstance(batch, list):
            batch = {k: torch.stack([_to_tensor(row[k]) for row in batch]) for k in _needed}
        else:
            batch = {k: _to_tensor(batch[k]) for k in _needed}
        y = _prepare(batch[target_col])
        x = torch.stack([batch[c].float() for c in feature_cols], dim=-1)
        return x, y

    return collate


# ---------------------------------------------------------------------------
# Pattern 1 — Offline batch query
# ---------------------------------------------------------------------------

def fetch_dataset(client: ChalkClient, dataset_name: str) -> "DataFrame":
    """
    Run offline_query and return a chalkdf DataFrame.

    On re-runs, Chalk skips the query and returns the cached dataset
    revision — no local files, no re-execution.
    """
    revision = client.offline_query(
        output=OUTPUT_FEATURES,
        dataset_name=dataset_name,
    )
    return revision.get_data_as_dataframe()


# ---------------------------------------------------------------------------
# Pattern 2a — Streaming DataLoader (low / medium scale)
# ---------------------------------------------------------------------------

def make_streaming_dataloader(
    client: ChalkClient,
    dataset_name: str,
    batch_size: int = 256,
    num_workers: int = 4,
) -> DataLoader:
    """
    Streaming DataLoader backed by create_torch_iter_dataset().

    Saves memory — PyTorch handles prefetch. Best when network bandwidth
    is not the bottleneck.
    """
    revision = client.offline_query(output=OUTPUT_FEATURES, dataset_name=dataset_name)
    return DataLoader(
        revision.create_torch_iter_dataset(),
        batch_size=batch_size,
        collate_fn=make_collate(_FEATURE_COLS, _TARGET_COL, lambda t: t.long()),
        num_workers=num_workers,
        prefetch_factor=4 if num_workers > 0 else None,
        persistent_workers=num_workers > 0,
        pin_memory=torch.cuda.is_available(),
    )


# ---------------------------------------------------------------------------
# Pattern 2b — Staged download + map-style DataLoader (large scale)
# ---------------------------------------------------------------------------

def make_map_dataloader(
    client: ChalkClient,
    dataset_name: str,
    local_dir: str | Path,
    batch_size: int = 256,
    num_workers: int = 8,
) -> DataLoader:
    """
    Download Parquet shards to local NVMe, then serve random-access
    batches via create_torch_map_dataset(). No network I/O in the
    training loop.
    """
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    revision = client.offline_query(output=OUTPUT_FEATURES, dataset_name=dataset_name)
    revision.download_data(str(local_dir))

    return DataLoader(
        revision.create_torch_map_dataset(),
        batch_size=batch_size,
        collate_fn=make_collate(_FEATURE_COLS, _TARGET_COL, lambda t: t.long()),
        shuffle=True,
        num_workers=num_workers,
        prefetch_factor=4 if num_workers > 0 else None,
        persistent_workers=num_workers > 0,
        pin_memory=torch.cuda.is_available(),
    )


# ---------------------------------------------------------------------------
# Pattern 3 — DDP multi-GPU
#
# Launch: torchrun --nproc_per_node=4 5_training.py
# ---------------------------------------------------------------------------

def make_ddp_dataloader(
    client: ChalkClient,
    dataset_name: str,
    local_dir: str | Path,
    batch_size: int = 256,
    num_workers: int = 4,
) -> tuple[DataLoader, DistributedSampler]:
    """
    Staged download + DistributedSampler for multi-GPU training.

    Each rank downloads the same shards; DistributedSampler assigns
    disjoint index subsets — no manual slicing needed.
    """
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    revision = client.get_dataset(dataset_name)
    revision.download_data(str(local_dir))
    ds = revision.create_torch_map_dataset()

    sampler = DistributedSampler(
        ds, num_replicas=dist.get_world_size(), rank=dist.get_rank(), shuffle=True,
    )
    loader = DataLoader(
        ds,
        batch_size=batch_size,
        sampler=sampler,
        collate_fn=make_collate(_FEATURE_COLS, _TARGET_COL, lambda t: t.long()),
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=num_workers > 0,
    )
    return loader, sampler
