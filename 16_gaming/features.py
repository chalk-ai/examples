"""
Shared feature definitions imported by resolvers, training, and inference.

data_model.py defines the gaming entity graph (Player, Match, etc.).
This file defines the ML feature class used by the preprocessing,
training, and inference examples.
"""

from chalk.features import features, _


@features
class PlayerFeatures:
    """Feature class for ML-based player scoring."""
    id: int
    engagement_score: float
    session_length: float
    win_rate: float
    player_tier: str
    region: str
    target: float

    # Transformed outputs — produced by the resolver in 4_preprocessing.py.
    engagement_scaled: float
    session_length_scaled: float
    win_rate_scaled: float
    player_tier_encoded: int
    region_encoded: int

    # Pattern A — Native expression scaling (no resolver, no artifact).
    # Population statistics are stored as features; the math runs in
    # Chalk's Rust/C++ vectorized engine.
    engagement_mean: float
    engagement_std: float
    engagement_expr_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std

    # Train/test split assignment — deterministic hash of id
    split: str  # "train" or "test" via hash-based bucketing
