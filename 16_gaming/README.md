# Gaming

Anti-cheat detection, bot fingerprinting, player risk scoring, and ML
training pipelines for any type of game. Chalk's feature
store handles the full lifecycle — from raw match telemetry to real-time
cheat scoring and model training with zero training-serving skew.

This example uses an FPS as the reference game, but the same patterns
extend to any genre — sports titles, battle royales, MOBAs, racing,
and other PvP or PvE games. Swap the stat names and thresholds;
the Chalk architecture stays the same.

## Data Model

Model match telemetry, player statistics, and sanction records as Chalk
features with `has_one` / `has_many` joins, expressions, and windowed
aggregations.

**[data_model.py](data_model.py)**

```python
@features
class Player:
    id: int
    matches: "DataFrame[Match]" = has_many(lambda: Player.id == Match.player_id)

    # Rolling cheat rate over 1d / 7d / 30d windows
    cheat_rate: Windowed[float] = windowed(
        "1d", "7d", "30d",
        expression=_.matches[
            _.sanction_record.is_flagged,
            _.time > _.chalk_window,
            _.time < _.chalk_now
        ].mean(),
        default=0
    )

@features
class Match:
    id: int
    player: Player = has_one(lambda: Player.id == Match.player_id)
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == Match.id)
    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == Match.id)

    # Chalk Expression — computed server-side with zero Python overhead
    is_long_session: bool = (
        F.unix_seconds(_.telemetry.session_end) - F.unix_seconds(_.telemetry.session_start)
    ) > 3600

@features
class SanctionRecord:
    # Expressions that derive rates from raw match stats — no resolver needed
    headshot_rate: float = feature(
        expression=_.stats.headshots / _.stats.kills,
        default=-1,
    )
    hit_accuracy: float = _.stats.shots_hit / _.stats.shots_fired
```

https://docs.chalk.ai/docs/features

## 1. Anti-Cheat Detection

Rule-based cheat detection combining aim anomalies with client
performance signals (FPS patterns, memory pause timing).

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

Behavioral fingerprinting from ADS (aim-down-sights) toggle patterns and
reaction time variance. Returns multiple features from a single resolver.

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

Push transformations into Chalk so training and inference never call
`transform_features()`. Prefer native expressions for arithmetic (they run in
Chalk's vectorized engine with zero Python overhead) and the Chalk Model
Registry for fitted models.

**[features.py](features.py)** — Pattern A: native expressions

```python
# Population stats stored as features — scaling runs entirely in Chalk's engine
engagement_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std
session_length_scaled: float = (_.session_length - _.session_length_mean) / _.session_length_std
win_rate_scaled: float = (_.win_rate - _.win_rate_mean) / _.win_rate_std
```

**[3_preprocessing.py](3_preprocessing.py)** — Pattern B: Chalk Model Registry

```python
from chalk.ml import ModelReference

categorical_encoder = ModelReference.from_alias(
    name="PlayerCategoricalEncoder", alias="latest",
)

@online
def encode_player_categoricals(
    player_tier: PlayerFeatures.player_tier,
    region: PlayerFeatures.region,
) -> Features[
    PlayerFeatures.player_tier_encoded,
    PlayerFeatures.region_encoded,
]:
    encoded = categorical_encoder.predict(np.array([[player_tier, region]]))[0]
    return PlayerFeatures(
        player_tier_encoded=int(encoded[0]),
        region_encoded=int(encoded[1]),
    )
```

https://docs.chalk.ai/docs/model-registry

## 4. PyTorch Training

Four patterns for feeding Chalk datasets into PyTorch training loops —
from simple batch queries to DDP multi-GPU.

**[4_training.py](4_training.py)**

```python
# Streaming DataLoader — no local files, no ETL
revision = client.offline_query(
    output=[PlayerFeatures.engagement_scaled, PlayerFeatures.session_length, PlayerFeatures.target],
    dataset_name="training_v1",
)
loader = DataLoader(revision.create_torch_iter_dataset(), batch_size=256, collate_fn=collate, num_workers=4)
```

https://docs.chalk.ai/docs/datasets

## 5. Online Inference

Serve pre-computed features to a trained model with zero training-serving
skew. Both `query()` and `query_bulk()` execute the same resolver DAG
as `offline_query`.

**[5_inference.py](5_inference.py)**

```python
# Same features, same values — online inference
result = client.query(
    input={PlayerFeatures.id: 42},
    output=[PlayerFeatures.engagement_scaled, PlayerFeatures.session_length],
)
values = [result.get_feature_value(f) or 0.0 for f in OUTPUT_FEATURES]
x = torch.tensor([values], dtype=torch.float32)
with torch.no_grad():
    return torch.sigmoid(model(x)).squeeze().item()
```

https://docs.chalk.ai/docs/query-basics
