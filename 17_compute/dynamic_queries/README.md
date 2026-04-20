# Dynamic Chalk Queries from an LLM Agent

Deploys a `@chalkcompute.function` that takes a `transaction_id`, lets
GPT-4o decide which Chalk features are worth fetching for a fraud-triage
verdict, pulls them via `POST /v1/query/online`, and returns a
structured JSON result. The LLM, the feature selection, and the Chalk
query all run inside an isolated container on Chalk compute.

Files:

- **[agent.py](agent.py)** — the `fraud-agent` function: image spec,
  OpenAI tool-use loop, and the Chalk query logic.
- **[catalog.py](catalog.py)** — the narrow allowlist of features the
  agent may request. Adapt to your own deployed features (see note below).
- **[run.py](run.py)** — client that invokes the deployed agent.

## Prerequisites

```bash
cp ../.env.example .env   # fill in CHALK_* + OPENAI_API_KEY
```

The features in `catalog.py` are specific to a `Transaction` + `User`
namespace. **To run this against your own Chalk deployment, edit
`catalog.py`** to reference features that exist in your environment and
have online resolvers / max_staleness set.

## Usage

```bash
# 1. Deploy the agent function (one-time; re-run to re-deploy)
uv run python agent.py

# 2. Invoke it on a transaction id
uv run python run.py 42
```

Example output:

```json
{
  "risk": "medium",
  "reasoning": "Amount is 3.8x the user's median; socure_score is elevated.",
  "features_used": [
    "transaction.amount",
    "transaction.user.median_transaction_amount",
    "transaction.user.socure_score"
  ]
}
```

## How it works

1. `run.py` calls the remote function by name.
2. Inside the container, the function exchanges `CHALK_CLIENT_*` for an
   access token (same flow a Chalk SDK client would do locally).
3. An OpenAI tool-use loop gives the LLM two tools:
   - `list_features()` → returns `FEATURE_CATALOG`
   - `query_chalk(feature_names)` → calls `/v1/query/online`
4. The loop terminates when the model emits a final JSON verdict or
   hits `MAX_TURNS`.

The agent is constrained to the allowlist so a prompt-injected
transaction_id can't exfiltrate features outside the catalog.
