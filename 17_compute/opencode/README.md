# OpenCode on a Chalk volume

Boot an [OpenCode](https://opencode.ai) server inside a Chalk container
with a git repo pre-loaded from a persistent Chalk volume. The volume is
mounted at `/root/code` via ChalkFS — no clone at container startup, so
subsequent boots are fast.

Files:

- **[populate_volume.py](populate_volume.py)** — clones any public git
  URL, creates a named Chalk volume, and uploads every file into it.
  Idempotent: re-run with the same `--volume` to refresh.
- **[opencode.py](opencode.py)** — launches a container from a Go + opencode
  base image, mounts the volume, starts `opencode serve`, prints the web URL.

## Prerequisites

```bash
cp ../.env.example .env    # fill in CHALK_* + ANTHROPIC_API_KEY
```

## Usage

```bash
# 1. Populate a volume (one-time per repo)
uv run python populate_volume.py https://github.com/chalk-ai/examples --volume chalk-examples

# 2. Launch the server against that volume
uv run python opencode.py --volume chalk-examples --timeout 2h
```

Output includes a `Web UI:` URL you can open in a browser and a
`opencode attach <url>` command for the TUI.

## Swapping the image

The base is `golang:1.24-bookworm` so the Go LSP works out of the box.
For a different language, change `OPENCODE_IMAGE` in `opencode.py`
(e.g. `python:3.12-slim`, `node:22-bookworm`, etc.).
