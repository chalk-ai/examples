"""
Anti-cheat resolver — rule-based cheat detection for competitive FPS.

Combines aim anomalies (headshot rate, hit accuracy) with client
performance signals (FPS drops, memory pause patterns) into a composite
cheat score. Runs as an @online resolver so it executes identically in
both offline_query (training) and online_query (serving).
"""

from chalk.features import online

from data_model import SanctionRecord


@online
def detect_cheating(
    headshot_rate: SanctionRecord.headshot_rate,
    hit_accuracy: SanctionRecord.hit_accuracy,
    kd_ratio: SanctionRecord.kd_ratio,
    low_fps_rate: SanctionRecord.telemetry.low_fps_rate,
    mem_pause_avg: SanctionRecord.telemetry.mem_pause_avg,
    mem_pause_freq: SanctionRecord.telemetry.mem_pause_freq,
) -> SanctionRecord.is_flagged:
    """
    Score a match session for cheat likelihood.

    Each signal contributes independently to a 0–1 composite score.
    Returns 1 (flagged) if score >= 0.6, else 0.
    """
    score = 0.0

    # Aimbot indicators — unnaturally precise aim
    if headshot_rate > 0.6:
        score += 0.2
    if hit_accuracy > 0.75:
        score += 0.15

    # Wallhack + aimbot combined — absurd kill-death ratio
    if kd_ratio > 8.0:
        score += 0.1

    # Frame rate anomalies — lag switch or spoofed telemetry
    if low_fps_rate > 0.4 or low_fps_rate == 0:
        score += 0.25

    # Memory anomalies — hooking or injection tools
    if mem_pause_avg < 2 or mem_pause_avg > 80 or mem_pause_freq > 40 or mem_pause_freq < 0.05:
        score += 0.35

    return 1 if score >= 0.6 else 0


# ---------------------------------------------------------------------------
# Unit tests — run with: pytest 1_anti_cheat.py
# ---------------------------------------------------------------------------

def test_clean_player_not_flagged():
    """Normal FPS stats should not trigger a flag."""
    assert detect_cheating(0.25, 0.35, 1.5, 0.1, 10.0, 1.0) == 0


def test_cheater_flagged():
    """Aimbot-level accuracy + suspicious FPS should flag."""
    assert detect_cheating(0.75, 0.85, 12.0, 0.5, 10.0, 1.0) == 1


def test_memory_anomaly_plus_fps():
    """Memory injection signals + FPS anomaly should flag."""
    assert detect_cheating(0.2, 0.3, 1.0, 0.0, 1.0, 60.0) == 1


def test_aim_anomalies_alone_not_enough():
    """Aim anomalies alone (0.45) should not reach the 0.6 threshold."""
    assert detect_cheating(0.75, 0.85, 12.0, 0.1, 10.0, 1.0) == 0
