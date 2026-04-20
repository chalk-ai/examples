"""Start the Temporal worker for the content moderation pipeline.

Requires a running Temporal server:
    temporal server start-dev
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from workflow import (
    TASK_QUEUE,
    ModerationWorkflow,
    classify_image_activity,
    policy_check_activity,
)

TEMPORAL_ADDRESS = "localhost:7233"


async def main() -> None:
    client = await Client.connect(TEMPORAL_ADDRESS)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ModerationWorkflow],
        activities=[classify_image_activity, policy_check_activity],
        activity_executor=ThreadPoolExecutor(max_workers=4),
    )
    print(f"Worker listening on task queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
