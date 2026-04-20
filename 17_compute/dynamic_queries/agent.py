"""Dynamic Chalk query from an OpenAI tool-use agent.

Deploys a `@chalkcompute.function` named `fraud_agent` that takes a
transaction_id, lets an LLM pick which Chalk features are worth fetching
for a fraud-triage decision, pulls them via `ChalkClient.query`, and
returns a structured verdict.

Run `python agent.py` once to deploy, then invoke via `run.py`.
"""

import logging
import os
from pathlib import Path

import chalkcompute


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

MODEL = "gpt-4o"
MAX_TURNS = 8

_CATALOG_SRC = str(Path(__file__).parent / "catalog.py")


@chalkcompute.function(
    name="fraud-agent",
    image=(
        chalkcompute.Image.debian_slim()
        .pip_install(["httpx", "openai>=1.40.0"])
        .add_local_file(_CATALOG_SRC, "/app/catalog.py")
    ),
    env={
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CHALK_CLIENT_ID": os.getenv("CHALK_CLIENT_ID"),
        "CHALK_CLIENT_SECRET": os.getenv("CHALK_CLIENT_SECRET"),
        "CHALK_ENVIRONMENT_ID": os.getenv("CHALK_ENVIRONMENT_ID"),
        "CHALK_API_SERVER": os.getenv("CHALK_API_SERVER"),
    },
)
def fraud_agent(transaction_id: int) -> str:
    import json as _json
    import os as _os

    import httpx
    from openai import OpenAI

    from catalog import FEATURE_CATALOG

    openai_client = OpenAI()

    api_server = _os.environ["CHALK_API_SERVER"].rstrip("/")
    env_id = _os.environ["CHALK_ENVIRONMENT_ID"]

    # Exchange client credentials once for an access token.
    token_resp = httpx.post(
        f"{api_server}/v1/oauth/token",
        json={
            "client_id": _os.environ["CHALK_CLIENT_ID"],
            "client_secret": _os.environ["CHALK_CLIENT_SECRET"],
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json()["access_token"]

    chalk_headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Chalk-Env-Id": env_id,
        "Content-Type": "application/json",
    }

    allowed = {f["name"] for f in FEATURE_CATALOG}

    def do_list_features() -> list[dict]:
        return FEATURE_CATALOG

    def do_query_chalk(feature_names: list[str]) -> dict:
        bad = [n for n in feature_names if n not in allowed]
        if bad:
            return {"error": f"features not in catalog: {bad}"}
        resp = httpx.post(
            f"{api_server}/v1/query/online",
            headers=chalk_headers,
            json={
                "inputs": {"transaction.id": transaction_id},
                "outputs": feature_names,
                "context": {"environment": env_id},
                "staleness": {},
                "include_meta": False,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            return {"error": f"chalk {resp.status_code}: {resp.text[:300]}"}
        payload = resp.json()
        values: dict[str, object] = {}
        for row in payload.get("data", []):
            name = row.get("field")
            if name in feature_names:
                values[name] = row.get("value", row.get("error"))
        for name in feature_names:
            values.setdefault(name, None)
        return values

    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_features",
                "description": (
                    "List every Chalk feature you are allowed to request, "
                    "with a description of what it means. Call this first."
                ),
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_chalk",
                "description": (
                    "Fetch a subset of features for the current transaction. "
                    "Pass only feature names returned by list_features. "
                    "Pick the minimal set that lets you decide."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feature_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Feature names to fetch, e.g. 'transaction.amount'.",
                        }
                    },
                    "required": ["feature_names"],
                },
            },
        },
    ]

    system = (
        "You are a fraud-triage agent. Given a transaction id, decide how risky "
        "the transaction is. You must call list_features first, then call "
        "query_chalk with a minimal relevant subset of feature names, then "
        "respond with a final JSON object of the form "
        '{"risk": "low"|"medium"|"high", "reasoning": str, "features_used": [str]}. '
        "Do not fetch features that are irrelevant to fraud risk."
    )
    user = f"Triage transaction_id={transaction_id}. Return the JSON verdict when done."

    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    for turn in range(MAX_TURNS):
        log.info("Turn %d", turn)
        resp = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            temperature=0,
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            content = msg.content or "{}"
            log.info("Final content: %s", content)
            try:
                verdict = _json.loads(content)
            except _json.JSONDecodeError:
                verdict = {"risk": "unknown", "reasoning": content, "features_used": []}
            return _json.dumps(verdict, default=str)

        for call in msg.tool_calls:
            args = _json.loads(call.function.arguments or "{}")
            log.info("Tool call: %s(%s)", call.function.name, args)
            if call.function.name == "list_features":
                result = do_list_features()
            elif call.function.name == "query_chalk":
                result = do_query_chalk(args.get("feature_names", []))
            else:
                result = {"error": f"unknown tool {call.function.name}"}
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": _json.dumps(result, default=str),
                }
            )

    return _json.dumps(
        {
            "risk": "unknown",
            "reasoning": f"agent did not finish within {MAX_TURNS} turns",
            "features_used": [],
        }
    )
