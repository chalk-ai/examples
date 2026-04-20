#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["chalkcompute>=1.1.1"]
# ///
"""
Deploy Gemma 3 4B on a GPU via vLLM, served as an OpenAI-compatible API.

Prerequisites:
    cp ../.env.example ../.env   # then fill in CHALK_* + HF_TOKEN
    HF_TOKEN needs huggingface.co access to google/gemma-3-4b-it.

Usage:
    uv run python serve.py
"""

from __future__ import annotations

import os
import sys
import time

# -- Load .env for Chalk credentials (checks ./, ../, ../../) ----------------

for _candidate in (
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
):
    if os.path.exists(_candidate):
        with open(_candidate) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
        break

# -- Config -------------------------------------------------------------------

MODEL = "google/gemma-3-4b-it"
PORT = 8000

# -- Image + ScalingGroup ----------------------------------------------------

from chalkcompute import ScalingGroup

sg = ScalingGroup(
    image="vllm/vllm-openai:latest",
    name="gemma-vllm",
    gpu="nvidia-l4:1",
    cpu="4",
    memory="16Gi",
    port=PORT,
    entrypoint=[
        "python3", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL,
        "--port", str(PORT),
        "--trust-remote-code",
        "--max-model-len", "4096",
        "--dtype", "bfloat16",
        "--gpu-memory-utilization", "0.90",
        "--enforce-eager",
    ],
    env={
        "HF_TOKEN": os.environ.get("HF_TOKEN", ""),
        "HF_HOME": "/root/.cache/huggingface",
    },
)

# -- Deploy and wait for vLLM health -----------------------------------------

print("Deploying scaling group (image build + GPU provisioning)...")
sg.deploy(build_timeout=600.0, ready_timeout=600.0)
print(f"Scaling group running: {sg.web_url}")

print("Waiting for vLLM to load the model...")
for _ in range(60):
    try:
        resp = sg.call("/health", method="GET", timeout=10)
        if resp.status_code == 200:
            break
    except Exception:
        pass
    time.sleep(15)
else:
    print("Timed out waiting for vLLM health check.")
    sys.exit(1)

# -- Test request (first call may be slow while the model warms up) -----------

print("Sending test completion...")
for attempt in range(10):
    resp = sg.call(
        "/v1/chat/completions",
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": "Say hello in one sentence."}],
            "max_tokens": 32,
        },
        timeout=120,
    )
    if resp.status_code == 200:
        break
    print(f"  attempt {attempt + 1}: {resp.status_code}, retrying...")
    time.sleep(15)
resp.raise_for_status()
print(f"Response: {resp.json()['choices'][0]['message']['content']}")

print(f"\nServing at: {sg.web_url}")
print(f"To tear down: sg.delete()")
