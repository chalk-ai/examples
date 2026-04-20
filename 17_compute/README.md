# Chalk Compute

Four patterns for running arbitrary Python, GPU workloads, and long-lived
services inside isolated Chalk containers with
[chalkcompute](https://pypi.org/project/chalkcompute/).

All examples assume a Chalk API key. Copy the env template once and fill
it in — each sub-example picks it up automatically:

```bash
cp .env.example .env   # at 17_compute/ root, or per-sub-example
```

## [opencode](opencode)

Pre-load a git repo into a persistent **Chalk volume**, then boot an
[OpenCode](https://opencode.ai) server inside a Chalk container with the
repo mounted at `/root/code`. The web UI + TUI connect over a public port.

```python
container = Container(
    image=OPENCODE_IMAGE,
    port=4096,
    volumes=[(volume_name, "/root/code")],
    env={"ANTHROPIC_API_KEY": ..., "OPENCODE_SERVER_PASSWORD": ...},
).run()
```

## [vllm](vllm)

Deploy Gemma 3 4B on a GPU via vLLM, served as an OpenAI-compatible API,
using a **`ScalingGroup`** for long-lived GPU-backed inference.

```python
sg = ScalingGroup(
    image="vllm/vllm-openai:latest",
    gpu="nvidia-l4:1",
    cpu="4", memory="16Gi", port=8000,
    entrypoint=["python3", "-m", "vllm.entrypoints.openai.api_server", "--model", MODEL, ...],
    env={"HF_TOKEN": ...},
)
sg.deploy()
resp = sg.call("/v1/chat/completions", json={...})
```

## [temporal](temporal)

Two-stage image moderation orchestrated by Temporal. Each stage is a
**`@chalkcompute.function`** running in its own container image; Temporal
owns all branching, thresholding, and human-in-the-loop signals.

```python
@chalkcompute.function(name="classify-image", image=Image.debian_slim()...pip_install([...]))
def classify_image(image_url: str) -> str:
    ...

# Temporal workflow activity:
classify = chalkcompute.RemoteFunction.from_name("classify-image")
return json.loads(classify(image_url))
```

## [dynamic_queries](dynamic_queries)

An OpenAI tool-use agent running inside a Chalk container decides which
Chalk features to fetch, issues dynamic `query/online` calls against the
Chalk API, and returns a structured verdict. Demonstrates how to compose
compute + online feature queries.

```python
@chalkcompute.function(name="fraud-agent", image=...)
def fraud_agent(transaction_id: int) -> str:
    # LLM picks from FEATURE_CATALOG, calls Chalk query, returns verdict
    ...
```
