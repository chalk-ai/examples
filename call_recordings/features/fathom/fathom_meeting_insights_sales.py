# trunk-ignore-all(ruff/W291)
from __future__ import annotations

from pydantic import BaseModel, Field


class StructuredOutputCallInsights(BaseModel):
    """Minimal schema matching the simple JSON format in the prompt.
    Prefer StructuredOutputCallInsights for richer analytics and UI.
    """

    reasons_for_meeting: str = Field(
        ...,
        description="""Plain-text reasons. Return "None" if there wan't anything mentioned.""",
    )
    risk_flag: str = Field(
        ...,
        description="""One-sentence risk summaries. Return "None" if there wan't anything mentioned.""",
    )


def prompt_meeting_insights_sales_user() -> str:
    return """
    You are analyzing a transcript of a B2B sales call between a representative from Chalk, a data infrastructure platform, and a prospective customer.
    Read the entire transcript carefully and extract the following insights in JSON format:

    1. **Reasons for Meeting** The stated reasons the prospect gave for agreeing to take the call or meet with Chalk. If none are stated explicitly, write `"None"`.
    2. **Risk Flag** Any risks raised by the prospect related to security, legal, or project timeline. If mentioned, summarize the risk in one sentence per item. If none, write `"None"`.

    **Output format**:
    ```json
    {
      "reasons_for_meeting": "string" or "None"
      "risk_flag": "string" or "None"
    }

    THE TRANSCRIPT TO ANALYZE:

    {{ FathomCall.transcript }}
    """
