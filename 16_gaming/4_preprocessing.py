"""
On-the-fly feature preprocessing for ML training and inference.

Three patterns for pushing transformations into Chalk so that training
and inference code never loads a .joblib or calls transform_features():

  Pattern A — Native Chalk expressions (see features.py)
    Store population statistics as features and write the formula as a
    Chalk expression. Runs in Chalk's Rust/C++ engine with zero Python
    overhead: engagement_scaled = (engagement_score - engagement_mean) / engagement_std

  Pattern B — @online resolvers with joblib artifacts (this file)
    For fitted sklearn objects (OrdinalEncoder, complex Pipelines), store
    the artifact alongside resolver code and load it once per worker.

  Pattern C — ONNX Model Registry (not shown)
    For heavy ML artifacts, export to ONNX and upload to Chalk's Model
    Registry. Chalk evaluates the ONNX graph internally during queries.
"""

import os
from functools import lru_cache

import joblib
import numpy as np
from chalk.features import Features, online
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

from features import PlayerFeatures


# ---------------------------------------------------------------------------
# Artifact loading — cached per worker process
# ---------------------------------------------------------------------------

_ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")


def _fallback_scaler() -> StandardScaler:
    s = StandardScaler()
    s.fit([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    return s


def _fallback_encoder() -> OrdinalEncoder:
    e = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    e.fit([["bronze", "na"], ["silver", "eu"], ["gold", "apac"]])
    return e


@lru_cache(maxsize=1)
def load_scaler():
    path = os.path.join(_ARTIFACTS_DIR, "standard_scaler.joblib")
    return joblib.load(path) if os.path.exists(path) else _fallback_scaler()


@lru_cache(maxsize=1)
def load_encoder():
    path = os.path.join(_ARTIFACTS_DIR, "ordinal_encoder.joblib")
    return joblib.load(path) if os.path.exists(path) else _fallback_encoder()


# ---------------------------------------------------------------------------
# Pattern B — sklearn artifact-based transformations
# ---------------------------------------------------------------------------

@online
def transform_player_features(
    engagement_score: PlayerFeatures.engagement_score,
    session_length: PlayerFeatures.session_length,
    win_rate: PlayerFeatures.win_rate,
    player_tier: PlayerFeatures.player_tier,
    region: PlayerFeatures.region,
) -> Features[
    PlayerFeatures.engagement_scaled,
    PlayerFeatures.session_length_scaled,
    PlayerFeatures.win_rate_scaled,
    PlayerFeatures.player_tier_encoded,
    PlayerFeatures.region_encoded,
]:
    """
    Apply StandardScaler + OrdinalEncoder via pre-fitted joblib artifacts.

    Artifacts load once per worker process. To retrain: refit offline,
    save as .joblib, run `chalk apply`. The next deploy picks them up.
    """
    scaled = load_scaler().transform(
        np.array([[engagement_score, session_length, win_rate]])
    )[0]
    encoded = load_encoder().transform(
        np.array([[player_tier, region]])
    )[0]

    return PlayerFeatures(
        engagement_scaled=float(scaled[0]),
        session_length_scaled=float(scaled[1]),
        win_rate_scaled=float(scaled[2]),
        player_tier_encoded=int(encoded[0]),
        region_encoded=int(encoded[1]),
    )
