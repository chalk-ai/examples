# Gaming

Anti-cheat detection, bot fingerprinting, player risk scoring, and ML
training pipelines built on Chalk.

Written against an FPS for the examples, but the same patterns work for
sports titles, MOBAs, battle royales, racing, and other PvP/PvE games —
swap the stat names and thresholds.

## Data Model

Entities, relationships, and ML features in one file.

**[data_model.py](data_model.py)**

```python
@features(owner="gaming-platform@chalk.ai", tags=["gaming", "anti-cheat"])
class Player:
    id: int
    matches: "DataFrame[Match]"

    cheat_rate: Windowed[float] = windowed(
        "1d", "7d", "30d",
        expression=_.matches[
            F.cast(_.sanction_record.is_flagged, int),
            _.time > _.chalk_window,
            _.time < _.chalk_now
        ].mean(),
        default=0,
    )

    engagement_score: float; win_rate: float; player_tier: str; region: str
    engagement_mean: float; engagement_std: float
    # Chalk Expression — guaranteed acceleration to C++ server-side
    engagement_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std
    player_tier_encoded: int  # written by the model resolver in 3_preprocessing.py

@features
class Match:
    id: int
    # Typed-FK has_one shorthand
    player_id: "Player.id"
    player: "Player"
    opponent_id: "Player.id"
    opponent: "Player"

    # FK lives on the child — join stays explicit
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == Match.id)
    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == Match.id)

    is_long_session: bool = (
        F.unix_seconds(_.telemetry.session_end) - F.unix_seconds(_.telemetry.session_start)
    ) > 3600

@features
class SanctionRecord:
    match_id: "Match.id"
    headshot_rate: float = feature(
        expression=_.stats.headshots / _.stats.kills,
        default=-1,
    )
    hit_accuracy: float = _.stats.shots_hit / _.stats.shots_fired
```

https://docs.chalk.ai/docs/features

## 1. Anti-Cheat Detection

Rule-based detection from aim anomalies and client performance signals.

**[1_anti_cheat.py](1_anti_cheat.py)**

```python
@online
def detect_cheating(
    headshot_rate: SanctionRecord.headshot_rate,
    hit_accuracy: SanctionRecord.hit_accuracy,
    kd_ratio: SanctionRecord.kd_ratio,
    low_fps_rate: SanctionRecord.telemetry.low_fps_rate,
    mem_pause_avg: SanctionRecord.telemetry.mem_pause_avg,
    mem_pause_freq: SanctionRecord.telemetry.mem_pause_freq,
) -> SanctionRecord.is_flagged:
    score = 0
    if headshot_rate > 0.6:
        score += 0.2
    if hit_accuracy > 0.75:
        score += 0.15
    if low_fps_rate > 0.4 or low_fps_rate == 0:
        score += 0.25
    if mem_pause_avg < 2 or mem_pause_avg > 80 or mem_pause_freq > 40:
        score += 0.35
    return 1 if score >= 0.6 else 0
```

https://docs.chalk.ai/docs/resolver-overview

## 2. Bot Detection

Behavioral fingerprinting from ADS toggle patterns and reaction time variance.

**[2_bot_detection.py](2_bot_detection.py)**

```python
@online
def detect_bot_behavior(
    scope_toggles_1: SanctionRecord.stats.scope_toggles_1,
    ...
    reaction_avg: SanctionRecord.stats.reaction_time_avg,
    reaction_min: SanctionRecord.stats.reaction_time_min,
    reaction_max: SanctionRecord.stats.reaction_time_max,
) -> Features[
    SanctionRecord.suspicious_aim,
    SanctionRecord.suspicious_reactions,
]:
    ...
```

https://docs.chalk.ai/docs/resolver-overview

## 3. Feature Preprocessing

Arithmetic transforms (scaling, normalization) as Chalk expressions on
the feature class. Fitted models (sklearn, XGBoost, ONNX) go through the
Model Registry and get wired up with a model resolver.

**[data_model.py](data_model.py)** — scaling via expression

```python
engagement_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std
session_length_scaled: float = (_.session_length - _.session_length_mean) / _.session_length_std
win_rate_scaled: float = (_.win_rate - _.win_rate_mean) / _.win_rate_std
```

**[3_preprocessing.py](3_preprocessing.py)** — model resolver

```python
from chalk import make_model_resolver
from chalk.ml import ModelReference

from data_model import Player

categorical_encoder = ModelReference.from_alias(
    name="PlayerCategoricalEncoder", alias="latest",
)

encode_player_categoricals = make_model_resolver(
    name="encode_player_categoricals",
    model=categorical_encoder,
    inputs=[Player.player_tier, Player.region],
    output=[Player.player_tier_encoded, Player.region_encoded],
)
```

https://docs.chalk.ai/docs/model_registry

## 4. PyTorch Training

Offline batch, streaming, and DDP patterns for feeding Chalk datasets
into PyTorch.

**[4_training.py](4_training.py)**

```python
revision = client.offline_query(
    output=[Player.engagement_scaled, Player.session_length, Player.target],
    dataset_name="training_v1",
)
loader = DataLoader(revision.create_torch_iter_dataset(), batch_size=256, collate_fn=collate, num_workers=4)
```

https://docs.chalk.ai/docs/datasets

## 5. Online Inference

Single-player and bulk scoring against the same feature contract used
during training.

**[5_inference.py](5_inference.py)**

```python
result = client.query(
    input={Player.id: 42},
    output=[Player.engagement_scaled, Player.session_length],
)
values = [result.get_feature_value(f) or 0.0 for f in OUTPUT_FEATURES]
x = torch.tensor([values], dtype=torch.float32)
with torch.no_grad():
    return torch.sigmoid(model(x)).squeeze().item()
```

https://docs.chalk.ai/docs/query-basics
