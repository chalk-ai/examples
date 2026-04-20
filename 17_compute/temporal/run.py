"""Start a content moderation workflow for an image.

Usage:
    python run.py <image_url>
    python run.py  # uses a default test image
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from temporalio.client import Client

from workflow import TASK_QUEUE, ModerationWorkflow

TEMPORAL_ADDRESS = "localhost:7233"

DEFAULT_IMAGE = "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg"


async def main() -> None:
    image_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE
    workflow_id = f"moderation-{uuid.uuid4().hex[:8]}"

    client = await Client.connect(TEMPORAL_ADDRESS)
    handle = await client.start_workflow(
        ModerationWorkflow.run,
        image_url,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    print(f"Workflow started: {workflow_id}")
    print(f"Image: {image_url}")

    result = await handle.result()

    print(f"\nStage 1 (ResNet): top_label={result.top_label}  confidence={result.top_confidence}")
    if result.policy_scores is None:
        print("Stage 2 (CLIP):  skipped (stage 1 was decisive)")
    else:
        scores = "  ".join(f"{k}={v:.2f}" for k, v in result.policy_scores.items())
        print(f"Stage 2 (CLIP):  {scores}")
    print(f"Decision: {result.decision}  reviewed_by: {result.reviewed_by}")
    if result.reviewed_by == "human":
        print(f"(signal sent via approve.py {workflow_id} <approved|rejected>)")


if __name__ == "__main__":
    asyncio.run(main())
