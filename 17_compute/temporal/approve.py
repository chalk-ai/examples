"""Send a human review decision to a running moderation workflow.

Usage:
    python approve.py <workflow_id> approved
    python approve.py <workflow_id> rejected
"""

from __future__ import annotations

import asyncio
import sys

from temporalio.client import Client

from workflow import ModerationWorkflow

TEMPORAL_ADDRESS = "localhost:7233"


async def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("approved", "rejected"):
        print("Usage: python approve.py <workflow_id> approved|rejected")
        sys.exit(1)

    workflow_id, decision = sys.argv[1], sys.argv[2]

    client = await Client.connect(TEMPORAL_ADDRESS)
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(ModerationWorkflow.review, decision)
    print(f"Sent '{decision}' to workflow {workflow_id}")


if __name__ == "__main__":
    asyncio.run(main())
