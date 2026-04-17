"""Bot detection from input telemetry."""

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
    suspicious_aim = False
    suspicious_reactions = False

    toggle_counts = [scope_toggles_1, scope_toggles_2, scope_toggles_3]
    durations = [scope_duration_1, scope_duration_2, scope_duration_3]
    total_toggles = sum(c for c in toggle_counts if c is not None)
    total_duration = sum(t for t in durations if t is not None)

    # Sub-0.3s per ADS toggle — faster than a human can aim.
    if total_toggles > 0 and total_duration / total_toggles < 0.3:
        suspicious_aim = True

    # Too-consistent window or impossibly fast average.
    if (reaction_max - reaction_min) < 40 or reaction_avg < 120:
        suspicious_reactions = True

    return SanctionRecord(
        suspicious_aim=suspicious_aim,
        suspicious_reactions=suspicious_reactions,
    )


# pytest 2_bot_detection.py

def test_normal_player():
    result = detect_bot_behavior(10, 8, 12, 5, 4, 6, 250, 180, 350)
    assert result.suspicious_aim is False
    assert result.suspicious_reactions is False


def test_bot_ads_pattern():
    result = detect_bot_behavior(100, 100, 100, 5, 5, 5, 250, 180, 350)
    assert result.suspicious_aim is True
    assert result.suspicious_reactions is False


def test_bot_reaction_times():
    result = detect_bot_behavior(10, 8, 12, 5, 4, 6, 100, 90, 110)
    assert result.suspicious_aim is False
    assert result.suspicious_reactions is True


def test_full_bot():
    result = detect_bot_behavior(100, 100, 100, 5, 5, 5, 50, 45, 55)
    assert result.suspicious_aim is True
    assert result.suspicious_reactions is True
