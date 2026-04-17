"""Online inference against Chalk."""

from __future__ import annotations

import numpy as np
import torch
from chalk.client import ChalkClient

from data_model import Player

OUTPUT_FEATURES = [
    Player.engagement_scaled,
    Player.session_length_scaled,
    Player.win_rate_scaled,
    Player.player_tier_encoded,
    Player.region_encoded,
]

FEATURE_NAMES = [
    "engagement_scaled", "session_length_scaled", "win_rate_scaled",
    "player_tier_encoded", "region_encoded",
]

_PREFIX = "player."


def score_player(
    client: ChalkClient,
    model: torch.nn.Module,
    entity_id: int,
    device: torch.device | str = "cpu",
) -> float:
    result = client.query(
        input={Player.id: entity_id},
        output=OUTPUT_FEATURES,
    )
    values = [result.get_feature_value(feat) or 0.0 for feat in OUTPUT_FEATURES]
    x = torch.tensor([values], dtype=torch.float32, device=device)

    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(x)).squeeze().item()


def score_players(
    client: ChalkClient,
    model: torch.nn.Module,
    entity_ids: list[int],
    device: torch.device | str = "cpu",
) -> list[float]:
    result = client.query_bulk(
        input={Player.id: entity_ids},
        output=OUTPUT_FEATURES,
    )

    pl_df = result.results[0].to_polars()
    if pl_df.is_empty():
        x = torch.zeros((len(entity_ids), len(FEATURE_NAMES)), dtype=torch.float32, device=device)
    else:
        prefix = _PREFIX if any(c.startswith(_PREFIX) for c in pl_df.columns) else ""
        arrays = [
            pl_df[f"{prefix}{col}"].fill_null(0).to_numpy().astype(np.float32)
            for col in FEATURE_NAMES
        ]
        x = torch.from_numpy(np.column_stack(arrays)).to(device)

    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(x)).squeeze(-1).tolist()


def verify_consistency(client: ChalkClient, entity_id: int) -> dict[str, tuple[float, float]]:
    """Assert online and offline queries return identical feature values."""
    online_result = client.query(
        input={Player.id: entity_id},
        output=OUTPUT_FEATURES,
    )
    offline_result = client.offline_query(
        input={Player.id: [entity_id]},
        output=OUTPUT_FEATURES,
    )
    offline_df = offline_result.get_data_as_pandas()
    prefix = _PREFIX if any(c.startswith(_PREFIX) for c in offline_df.columns) else ""

    comparison = {}
    for feat, name in zip(OUTPUT_FEATURES, FEATURE_NAMES):
        online_val = float(online_result.get_feature_value(feat) or 0.0)
        offline_val = float(offline_df[f"{prefix}{name}"].iloc[0] or 0.0)
        comparison[name] = (online_val, offline_val)
        assert online_val == offline_val, f"Mismatch: {name} online={online_val} offline={offline_val}"

    return comparison
