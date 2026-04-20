"""End-to-end tests for the two-stage content moderation pipeline.

Deploys both Chalk functions (classify-image, policy-check) and verifies
they can each be invoked directly. The Temporal workflow is exercised
manually via run.py + approve.py — see README.
"""

import os
import subprocess
import sys

import pytest
from dotenv import load_dotenv

load_dotenv()

CHALK_CLIENT_ID = os.environ.get("CHALK_CLIENT_ID", "")
CHALK_API_SERVER = os.environ.get("CHALK_API_SERVER", "")

needs_staging = pytest.mark.skipif(
    not CHALK_CLIENT_ID or not CHALK_API_SERVER,
    reason="CHALK_CLIENT_ID/CHALK_API_SERVER not set",
)

EXAMPLE_DIR = os.path.dirname(__file__)

TEST_IMAGE_URL = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg"

EXPECTED_POLICIES = {"violence", "adult", "weapon", "minor"}


def _deploy_script(script_name: str) -> None:
    """Run a deploy script as a subprocess."""
    result = subprocess.run(
        [sys.executable, os.path.join(EXAMPLE_DIR, script_name)],
        capture_output=True,
        text=True,
        env=os.environ,
        timeout=600,
    )
    if result.returncode != 0:
        pytest.fail(
            f"{script_name} deploy failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout[-500:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )


@needs_staging
def test_classify_returns_predictions() -> None:
    """Deploy classify_image and verify it returns labeled predictions."""
    import json

    _deploy_script("classify.py")

    import chalkcompute

    classify = chalkcompute.RemoteFunction.from_name("classify-image")
    result = json.loads(classify(TEST_IMAGE_URL))

    assert len(result["labels"]) > 0
    assert isinstance(result["top_label"], str)
    assert isinstance(result["top_confidence"], float)
    assert 0.0 <= result["top_confidence"] <= 1.0
    # needs_review is no longer part of the stage-1 contract — Temporal owns thresholds.
    assert "needs_review" not in result


@needs_staging
def test_classify_identifies_known_image() -> None:
    """The test image is a cat — the model should classify it as such."""
    import json

    import chalkcompute

    classify = chalkcompute.RemoteFunction.from_name("classify-image")
    result = json.loads(classify(TEST_IMAGE_URL))

    all_labels = [lbl["label"].lower() for lbl in result["labels"]]
    cat_labels = [name for name in all_labels if "cat" in name or "tabby" in name or "egyptian" in name]
    assert len(cat_labels) > 0, f"Expected cat-related label, got: {all_labels}"


@needs_staging
def test_policy_check_returns_per_policy_scores() -> None:
    """Deploy policy_check and verify it returns the expected policy schema."""
    import json

    _deploy_script("policy_check.py")

    import chalkcompute

    policy = chalkcompute.RemoteFunction.from_name("policy-check")
    result = json.loads(policy(TEST_IMAGE_URL))

    assert set(result["policy_scores"].keys()) == EXPECTED_POLICIES
    for key, score in result["policy_scores"].items():
        assert isinstance(score, float), f"{key} score is not a float"
        assert 0.0 <= score <= 1.0, f"{key}={score} out of [0, 1]"

    assert result["max_policy"] in EXPECTED_POLICIES
    assert result["max_score"] == max(result["policy_scores"].values())
