"""
Gaming data model — feature classes for competitive FPS games.

Demonstrates has_one, has_many, Chalk expressions, and windowed aggregations
applied to match telemetry, player statistics, and anti-cheat scoring.
"""

from datetime import datetime

from chalk.features import features, _, DataFrame, has_one, has_many, Primary, feature
from chalk.streams import windowed, Windowed
import chalk.functions as F


@features
class Player:
    id: int

    # A player has many matches — Chalk resolves the join automatically.
    # https://docs.chalk.ai/docs/has-many
    matches: "DataFrame[Match]" = has_many(lambda: Player.id == Match.player_id)

    # Windowed aggregation: rolling cheat rate over 1d / 7d / 30d windows.
    # Chalk evaluates this expression server-side in its vectorized engine
    # on every query — no cron job, no materialization lag.
    # https://docs.chalk.ai/docs/aggregations
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

    # Two foreign keys to the same Player class — use explicit has_one().
    # https://docs.chalk.ai/docs/has-one
    player_id: int
    player: Player = has_one(lambda: Player.id == Match.player_id)
    opponent_id: int
    opponent: Player = has_one(lambda: Player.id == Match.opponent_id)

    # Related entities joined by match id.
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == Match.id)
    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == Match.id)
    sanction_record: "SanctionRecord" = has_one(lambda: SanctionRecord.match_id == Match.id)

    time: datetime

    # Chalk Expression — computed server-side with zero Python overhead.
    # https://docs.chalk.ai/docs/expression
    is_long_session: bool = (
        F.unix_seconds(_.telemetry.session_end) - F.unix_seconds(_.telemetry.session_start)
    ) > 3600


@features
class SanctionRecord:
    id: int
    match_id: Match.id
    match: Match

    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == SanctionRecord.match_id)
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == SanctionRecord.match_id)

    # Expressions that derive rates from raw match stats — no resolver needed.
    # Chalk evaluates these in its Rust/C++ engine during both offline and online queries.
    headshot_rate: float = feature(
        expression=_.stats.headshots / _.stats.kills,
        default=-1,
    )
    hit_accuracy: float = _.stats.shots_hit / _.stats.shots_fired
    kd_ratio: float = _.stats.kills / _.stats.deaths

    # Computed by Python resolvers (see 2_anti_cheat.py and 3_bot_detection.py).
    is_flagged: int
    suspicious_aim: bool
    suspicious_reactions: bool


@features
class Telemetry:
    match_id: Primary[Match.id]

    is_bot_lobby: int
    match_duration: int
    player_level: int
    player_xp: int
    player_rank: int

    device_name: str
    end_reason: str
    match_result: str

    # Performance telemetry — used for cheat detection.
    low_fps_rate: float
    mem_pause_avg: float
    mem_pause_freq: float

    session_end: datetime
    session_start: datetime


@features
class MatchStats:
    """Per-match gameplay statistics (150+ columns in a real deployment)."""
    match_id: Primary[Match.id]
    player_id: Player.id

    # Combat
    kills: int
    deaths: int
    assists: int
    headshots: int
    shots_fired: int
    shots_hit: int

    # Damage
    damage_dealt: int
    damage_taken: int

    # Objectives
    objectives_completed: int
    objectives_played: int
    plants: int
    defuses: int

    # Movement
    distance_traveled: int
    time_alive: int

    # Scope / ADS telemetry — used for bot detection.
    scope_toggles_1: int
    scope_duration_1: int
    scope_toggles_2: int
    scope_duration_2: int
    scope_toggles_3: int
    scope_duration_3: int
    reaction_time_avg: int
    reaction_time_min: int
    reaction_time_max: int
    input_count: int

    # Metadata
    platform: str
    country: str
    rank: int
    time: datetime
