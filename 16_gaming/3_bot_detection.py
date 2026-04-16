"""
Bot detection resolver — behavioral fingerprinting from input telemetry.

Analyzes ADS (aim-down-sights) toggle patterns and reaction time variance
to distinguish human players from automated bots. Returns multiple features
from a single resolver using Chalk's Features[] multi-output pattern.
"""

from chalk.features import online, Features

from data_model import SanctionRecord


@online
def detect_bot_behavior(
    scope_toggles_1: SanctionRecord.stats.scope_toggles_1,
    scope_toggles_2: SanctionRecord.stats.scope_toggles_2,
    scope_toggles_3: SanctionRecord.stats.scope_toggles_3,
    scope_duration_1: SanctionRecord.stats.scope_duration_1,
    scope_duration_2: SanctionRecord.stats.scope_duration_2,
    scope_duration_3: SanctionRecord.stats.scope_duration_3,
    reaction_avg: SanctionRecord.stats.reaction_time_avg,
    reaction_min: SanctionRecord.stats.reaction_time_min,
    reaction_max: SanctionRecord.stats.reaction_time_max,
) -> Features[
    SanctionRecord.suspicious_aim,
    SanctionRecord.suspicious_reactions,
]:
    """
    Analyze input telemetry for bot-like behavior patterns.

    ADS patterns: bots snap in and out of scope at inhuman speed,
    producing very low average time per ADS toggle (< 0.3s).

    Reaction times: bots produce unnaturally consistent reaction times
    (max - min < 40ms) or impossibly fast averages (< 120ms).
    """
    suspicious_aim = False
    suspicious_reactions = False

    # ADS toggle analysis
    toggle_counts = [scope_toggles_1, scope_toggles_2, scope_toggles_3]
    durations = [scope_duration_1, scope_duration_2, scope_duration_3]

    total_toggles = sum(c for c in toggle_counts if c is not None)
    total_duration = sum(t for t in durations if t is not None)

    if total_toggles > 0 and total_duration / total_toggles < 0.3:
        suspicious_aim = True

    # Reaction time variance analysis
    if (reaction_max - reaction_min) < 40 or reaction_avg < 120:
        suspicious_reactions = True

    return SanctionRecord(
        suspicious_aim=suspicious_aim,
        suspicious_reactions=suspicious_reactions,
    )


# ---------------------------------------------------------------------------
# Unit tests — run with: pytest 3_bot_detection.py
# ---------------------------------------------------------------------------

def test_normal_player():
    """Human-like ADS and reaction patterns should not flag."""
    result = detect_bot_behavior(10, 8, 12, 5, 4, 6, 250, 180, 350)
    assert result.suspicious_aim is False
    assert result.suspicious_reactions is False


def test_bot_ads_pattern():
    """Rapid ADS toggling (avg < 0.3s per toggle) should flag aim."""
    result = detect_bot_behavior(100, 100, 100, 5, 5, 5, 250, 180, 350)
    assert result.suspicious_aim is True
    assert result.suspicious_reactions is False


def test_bot_reaction_times():
    """Unnaturally consistent reactions (range < 40ms) should flag reactions."""
    result = detect_bot_behavior(10, 8, 12, 5, 4, 6, 100, 90, 110)
    assert result.suspicious_aim is False
    assert result.suspicious_reactions is True


def test_full_bot():
    """Both ADS and reaction anomalies should flag both."""
    result = detect_bot_behavior(100, 100, 100, 5, 5, 5, 50, 45, 55)
    assert result.suspicious_aim is True
    assert result.suspicious_reactions is True
