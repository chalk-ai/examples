"""
Shared feature definitions imported by resolvers, training, and inference.

data_model.py defines the gaming entity graph (Player, Match, etc.).
This file defines the ML feature class used by preprocessing, training,
and inference.

Scaling is pushed into Chalk expressions — the arithmetic runs in Chalk's
vectorized engine with zero Python overhead, and the same formula is
guaranteed to run identically during offline_query (training) and
online query (inference). Population statistics are stored as features
so the formulas stay expressions.
"""

from chalk.features import features, _


@features
class PlayerFeatures:
    """Feature class for ML-based player scoring."""
    id: int

    # Raw inputs
    engagement_score: float
    session_length: float
    win_rate: float
    player_tier: str
    region: str
    target: float

    # Population statistics — refreshed periodically by a scheduled resolver.
    # Stored as features so the scaling formulas can stay as expressions.
    engagement_mean: float
    engagement_std: float
    session_length_mean: float
    session_length_std: float
    win_rate_mean: float
    win_rate_std: float

    # Pattern A — Native expressions. Evaluated in Chalk's vectorized engine;
    # no Python, no sklearn, no joblib. Identical in offline_query and online.
    # https://docs.chalk.ai/docs/expression
    engagement_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std
    session_length_scaled: float = (_.session_length - _.session_length_mean) / _.session_length_std
    win_rate_scaled: float = (_.win_rate - _.win_rate_mean) / _.win_rate_std

    # Categorical encodings — fit offline and served via Chalk Model Registry
    # (see 3_preprocessing.py). Written by the resolver there.
    player_tier_encoded: int
    region_encoded: int

    # Train/test split assignment — deterministic hash of id.
    split: str  # "train" or "test" via hash-based bucketing
