# vLLM on a Chalk GPU ScalingGroup

Deploy Gemma 3 4B behind an OpenAI-compatible chat API on an
`nvidia-l4` GPU via `chalkcompute.ScalingGroup`. The scaling group owns
the container image, the GPU allocation, and an inbound HTTPS endpoint.

**[serve.py](serve.py)** — one script to deploy + health-check + test.

## Prerequisites

```bash
cp ../.env.example .env   # fill in CHALK_* + HF_TOKEN
```

`HF_TOKEN` needs huggingface.co access approved for `google/gemma-3-4b-it`.

## Usage

```bash
uv run python serve.py
```

The script blocks until vLLM passes `/health`, sends one test chat
completion, and prints the `web_url` of the live endpoint. Teardown:

```python
from chalkcompute import ScalingGroup
sg = ScalingGroup.from_name("gemma-vllm")
sg.delete()
```

## Swapping the model

Change `MODEL` at the top of `serve.py`. For larger models, bump
`gpu=` (e.g. `nvidia-a100:1`) and `--max-model-len`.
