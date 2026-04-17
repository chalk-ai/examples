"""
Preprocessing via Chalk's Model Registry.

Arithmetic (scaling, normalization) is expressed on `Player` in
data_model.py and runs server-side. This file handles what actually
needs a fitted model: categorical encoding via a registered OrdinalEncoder.

https://docs.chalk.ai/docs/model_registry
"""

from chalk import make_model_resolver
from chalk.ml import ModelReference

from data_model import Player


# Registration is a one-time offline step. Sketch:
#
#   from sklearn.preprocessing import OrdinalEncoder
#   encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
#   encoder.fit(df[["player_tier", "region"]])
#   client.register_model_version(
#       name="PlayerCategoricalEncoder",
#       model=encoder,
#       model_type=ModelType.SKLEARN,
#       model_encoding=ModelEncoding.PICKLE,
#       aliases=["latest"],
#       input_features=[Player.player_tier, Player.region],
#       output_features=[Player.player_tier_encoded, Player.region_encoded],
#   )

categorical_encoder = ModelReference.from_alias(
    name="PlayerCategoricalEncoder",
    alias="latest",
)

encode_player_categoricals = make_model_resolver(
    name="encode_player_categoricals",
    model=categorical_encoder,
    inputs=[Player.player_tier, Player.region],
    output=[Player.player_tier_encoded, Player.region_encoded],
)
