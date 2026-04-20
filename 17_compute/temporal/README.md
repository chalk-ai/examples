# Content Moderation — Temporal + Chalk

Two-stage image moderation in isolated Chalk containers, orchestrated
end-to-end by [Temporal](https://temporal.io) with human-in-the-loop
approval for ambiguous results.

- **Stage 1 — `classify-image`**: ResNet-50 supervised classification (top-5 labels).
- **Stage 2 — `policy-check`**: CLIP zero-shot scoring against a fixed policy prompt list (`violence`, `adult`, `weapon`, `minor`).
- **Orchestration**: Temporal owns all branching, thresholds, and the HITL signal — the Chalk functions just do ML.

## Prerequisites

```bash
cp ../.env.example .env           # fill in CHALK_*
brew install temporal             # Temporal CLI for the dev server
```

## Quick start

### 1. Deploy both Chalk functions

```bash
set -a && source .env && set +a
uv run python classify.py        # stage 1 — ResNet
uv run python policy_check.py    # stage 2 — CLIP zero-shot
```

Each is a serverless function on Chalk in its own container image
(debian_slim + CPU torch + transformers). Untrusted images are
downloaded and processed entirely inside the sandbox — the caller never
handles raw bytes.

### 2. Start Temporal

```bash
temporal server start-dev
```

Web UI at http://localhost:8233.

### 3. Start the worker

```bash
set -a && source .env && set +a
uv run python worker.py
```

### 4. Submit an image for moderation

```bash
uv run python run.py https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg
```

The workflow branches on stage-1 confidence:

| Stage-1 confidence | Action |
|---|---|
| `≥ 0.85` | Auto-approve (skip stage 2) |
| `< 0.5`  | Auto-reject (skip stage 2) |
| `0.5 – 0.85` | Run CLIP policy check; if every policy `< 0.5` → auto-approve, else wait for human |

### 5. Approve or reject (human-in-the-loop)

Triggered only when stage 2 flags at least one policy.

**Option A — Temporal web UI:**

1. Open http://localhost:8233
2. Click on your workflow (e.g. `moderation-abc123`)
3. Click **Signal** (top-right)
4. Signal name: `review`
5. Input: `"approved"` or `"rejected"`
6. Click Send

**Option B — CLI:**

```bash
uv run python approve.py <workflow_id> approved
uv run python approve.py <workflow_id> rejected
```

## Architecture

```
Temporal Server
  └─ ModerationWorkflow
       ├─ Activity: classify_image_activity
       │    └─ Chalk RemoteFunction "classify-image"  (ResNet-50)
       ├─ Branch on stage-1 confidence:
       │    ≥ 0.85  → auto_approved
       │    < 0.5   → auto_rejected
       │    else    ↓
       ├─ Activity: policy_check_activity
       │    └─ Chalk RemoteFunction "policy-check"    (CLIP zero-shot)
       ├─ If max(policy_scores) < 0.5 → auto_approved
       └─ Else: workflow.wait_condition (human signal, 24h timeout)
```

## Testing

Tests deploy both functions and invoke each directly (no Temporal server needed):

```bash
uv run python -m pytest test_content_moderation.py -v
```
