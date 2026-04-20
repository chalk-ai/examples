"""Temporal workflow for content moderation with human-in-the-loop.

The workflow:
1. Calls Chalk classify_image (ResNet, runs in an isolated container).
2. If stage-1 confidence >= AUTO_APPROVE_THRESHOLD: auto-approve.
3. If stage-1 confidence <  AUTO_REJECT_THRESHOLD:  auto-reject.
4. Otherwise (borderline): calls Chalk policy_check (CLIP zero-shot).
   - If no policy fires (>= POLICY_FLAG_THRESHOLD): auto-approve.
   - Else: pause and wait for a human signal.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow

AUTO_APPROVE_THRESHOLD = 0.85
AUTO_REJECT_THRESHOLD = 0.5
POLICY_FLAG_THRESHOLD = 0.5
REVIEW_TIMEOUT = timedelta(hours=24)
TASK_QUEUE = "content-moderation"


@dataclass
class ModerationResult:
    top_label: str
    top_confidence: float
    policy_scores: dict[str, float] | None
    decision: str
    reviewed_by: str


@activity.defn
def classify_image_activity(image_url: str) -> dict:
    """Stage 1: ResNet classification inside a Chalk container."""
    import json

    import chalkcompute

    classify = chalkcompute.RemoteFunction.from_name("classify-image")
    return json.loads(classify(image_url))


@activity.defn
def policy_check_activity(image_url: str) -> dict:
    """Stage 2: CLIP zero-shot policy scoring inside a Chalk container."""
    import json

    import chalkcompute

    policy = chalkcompute.RemoteFunction.from_name("policy-check")
    return json.loads(policy(image_url))


@workflow.defn
class ModerationWorkflow:
    """Two-stage classification with thresholded branching and HITL fallback."""

    def __init__(self) -> None:
        self._decision: str | None = None

    @workflow.run
    async def run(self, image_url: str) -> ModerationResult:
        # Stage 1: ResNet
        stage1 = await workflow.execute_activity(
            classify_image_activity,
            image_url,
            start_to_close_timeout=timedelta(minutes=5),
        )
        top_label = stage1["top_label"]
        top_confidence = stage1["top_confidence"]

        # Confident enough → auto-approve
        if top_confidence >= AUTO_APPROVE_THRESHOLD:
            return ModerationResult(
                top_label=top_label, top_confidence=top_confidence,
                policy_scores=None, decision="auto_approved", reviewed_by="model",
            )

        # Confident enough the other way → auto-reject
        if top_confidence < AUTO_REJECT_THRESHOLD:
            return ModerationResult(
                top_label=top_label, top_confidence=top_confidence,
                policy_scores=None, decision="auto_rejected", reviewed_by="model",
            )

        # Borderline → Stage 2: CLIP zero-shot policy check
        workflow.logger.info(
            "Borderline stage-1 (label=%s confidence=%.2f) — running policy check",
            top_label, top_confidence,
        )
        stage2 = await workflow.execute_activity(
            policy_check_activity,
            image_url,
            start_to_close_timeout=timedelta(minutes=5),
        )
        policy_scores: dict[str, float] = stage2["policy_scores"]

        # No policy fired → auto-approve
        if max(policy_scores.values()) < POLICY_FLAG_THRESHOLD:
            return ModerationResult(
                top_label=top_label, top_confidence=top_confidence,
                policy_scores=policy_scores, decision="auto_approved",
                reviewed_by="policy_check",
            )

        # A policy fired → wait for a human reviewer
        workflow.logger.info(
            "Policy flagged — waiting for human review. max_policy=%s score=%.2f",
            stage2["max_policy"], stage2["max_score"],
        )
        try:
            await workflow.wait_condition(
                lambda: self._decision is not None,
                timeout=REVIEW_TIMEOUT,
            )
            decision = self._decision
            reviewed_by = "human"
        except asyncio.TimeoutError:
            decision = "auto_rejected"
            reviewed_by = "timeout"

        return ModerationResult(
            top_label=top_label, top_confidence=top_confidence,
            policy_scores=policy_scores, decision=decision, reviewed_by=reviewed_by,
        )

    @workflow.signal
    def review(self, decision: str) -> None:
        """Signal from a human reviewer: 'approved' or 'rejected'."""
        self._decision = decision
