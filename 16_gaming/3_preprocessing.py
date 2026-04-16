"""
Feature preprocessing for ML training and inference.

Chalk offers three places to run transformations. Pick the highest-level
pattern that fits the feature — each layer down adds Python overhead.

  Pattern A — Native expressions (preferred)
    Arithmetic formulas evaluated in Chalk's vectorized engine. Zero
    Python, identical in offline_query and online. Used for the three
    scaled numerics — see features.py.

  Pattern B — @online resolver + Chalk Model Registry (this file)
    For fitted sklearn / XGBoost / ONNX / etc. models. Chalk manages
    upload, versioning, and per-worker loading. The resolver just calls
    `.predict()`. Used below for categorical encoding — the one thing
    that genuinely needs a fitted model.
    https://docs.chalk.ai/docs/model-registry

  Pattern C — @online resolver + local joblib file
    Fallback when the artifact can't go through the Model Registry
    (private deps, exotic formats). You manage the file and the loader
    yourself. Not shown — use sparingly.
"""

import numpy as np
from chalk.features import Features, online
from chalk.ml import ModelReference

from features import PlayerFeatures


# ---------------------------------------------------------------------------
# Model Registry reference
#
# One-time registration (from an offline training script):
#
#   from chalk.client import ChalkClient
#   from chalk.ml import ModelType, ModelEncoding
#   from sklearn.preprocessing import OrdinalEncoder
#
#   encoder = OrdinalEncoder(
#       handle_unknown="use_encoded_value", unknown_value=-1,
#   )
#   encoder.fit(training_df[["player_tier", "region"]])
#
#   client = ChalkClient()
#   client.register_model_namespace(
#       name="PlayerCategoricalEncoder",
#       description="Ordinal encoder for player_tier and region",
#   )
#   client.register_model_version(
#       name="PlayerCategoricalEncoder",
#       model=encoder,
#       model_type=ModelType.SKLEARN,
#       model_encoding=ModelEncoding.PICKLE,
#       aliases=["latest"],
#   )
#
# Chalk loads the referenced model into each worker once at deploy time.
# To roll back: register a new version and swap the alias.
# ---------------------------------------------------------------------------

categorical_encoder = ModelReference.from_alias(
    name="PlayerCategoricalEncoder",
    alias="latest",
)


@online
def encode_player_categoricals(
    player_tier: PlayerFeatures.player_tier,
    region: PlayerFeatures.region,
) -> Features[
    PlayerFeatures.player_tier_encoded,
    PlayerFeatures.region_encoded,
]:
    """
    Categorical encoding via the registered OrdinalEncoder.

    Everything else (engagement_scaled, session_length_scaled,
    win_rate_scaled) is a native Chalk expression in features.py —
    this resolver only handles what expressions can't.
    """
    encoded = categorical_encoder.predict(
        np.array([[player_tier, region]])
    )[0]
    return PlayerFeatures(
        player_tier_encoded=int(encoded[0]),
        region_encoded=int(encoded[1]),
    )
