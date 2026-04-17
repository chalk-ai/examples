"""Gaming data model — entities, relationships, ML features."""

from datetime import datetime

from chalk.features import features, _, DataFrame, has_one, Primary, feature
from chalk.streams import windowed, Windowed
import chalk.functions as F


@features(
    owner="gaming-platform@chalk.ai",
    tags=["gaming", "anti-cheat"],
)
class Player:
    id: int
    matches: "DataFrame[Match]"

    # Rolling cheat rate, evaluated at query time.
    # https://docs.chalk.ai/docs/aggregations
    cheat_rate: Windowed[float] = windowed(
        "1d", "7d", "30d",
        expression=_.matches[
            F.cast(_.sanction_record.is_flagged, int),
            _.time > _.chalk_window,
            _.time < _.chalk_now
        ].mean(),
        default=0
    )

    engagement_score: float
    session_length: float
    win_rate: float
    player_tier: str
    region: str
    target: float

    # Population stats, refreshed by a scheduled resolver.
    engagement_mean: float
    engagement_std: float
    session_length_mean: float
    session_length_std: float
    win_rate_mean: float
    win_rate_std: float

    # Chalk Expression — guaranteed acceleration to C++ server-side.
    engagement_scaled: float = (_.engagement_score - _.engagement_mean) / _.engagement_std
    session_length_scaled: float = (_.session_length - _.session_length_mean) / _.session_length_std
    win_rate_scaled: float = (_.win_rate - _.win_rate_mean) / _.win_rate_std

    # Written by the model resolver in 3_preprocessing.py.
    player_tier_encoded: int
    region_encoded: int

    split: str


@features
class Match:
    id: int

    # Typed-FK has_one. https://docs.chalk.ai/docs/has-one
    player_id: "Player.id"
    player: "Player"
    opponent_id: "Player.id"
    opponent: "Player"

    # Reverse has_one — FK is on the child.
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == Match.id)
    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == Match.id)
    sanction_record: "SanctionRecord" = has_one(lambda: SanctionRecord.match_id == Match.id)

    time: datetime

    # Chalk Expression — guaranteed acceleration to C++ server-side.
    is_long_session: bool = (
        F.unix_seconds(_.telemetry.session_end) - F.unix_seconds(_.telemetry.session_start)
    ) > 3600


@features
class SanctionRecord:
    id: int
    match_id: "Match.id"
    match: "Match"

    telemetry: "Telemetry" = has_one(lambda: Telemetry.match_id == SanctionRecord.match_id)
    stats: "MatchStats" = has_one(lambda: MatchStats.match_id == SanctionRecord.match_id)

    headshot_rate: float = feature(
        expression=_.stats.headshots / _.stats.kills,
        default=-1,
    )
    hit_accuracy: float = _.stats.shots_hit / _.stats.shots_fired
    kd_ratio: float = _.stats.kills / _.stats.deaths

    # Written by resolvers in 1_anti_cheat.py and 2_bot_detection.py.
    is_flagged: int
    suspicious_aim: bool
    suspicious_reactions: bool


@features
class Telemetry:
    match_id: Primary["Match.id"]

    is_bot_lobby: int
    match_duration: int
    player_level: int
    player_xp: int
    player_rank: int

    device_name: str
    end_reason: str
    match_result: str

    low_fps_rate: float
    mem_pause_avg: float
    mem_pause_freq: float

    session_end: datetime
    session_start: datetime


@features
class MatchStats:
    """150+ columns in a real deployment."""
    match_id: Primary["Match.id"]
    player_id: "Player.id"

    kills: int
    deaths: int
    assists: int
    headshots: int
    shots_fired: int
    shots_hit: int

    damage_dealt: int
    damage_taken: int

    objectives_completed: int
    objectives_played: int
    plants: int
    defuses: int

    distance_traveled: int
    time_alive: int

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

    platform: str
    country: str
    rank: int
    time: datetime
