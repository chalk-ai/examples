#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "python-dotenv"]
# ///
"""Populate a Chalk volume with the contents of a git repo.

Clones a public git URL to a temp dir, then uploads every file to a named
Chalk volume. Re-run with the same --volume to refresh. Pair with
opencode.py, which mounts the volume at /root/code inside a container.

Usage:
    uv run python populate_volume.py https://github.com/chalk-ai/examples --volume chalk-examples

Requires CHALK_CLIENT_ID / CHALK_CLIENT_SECRET / CHALK_ENVIRONMENT_ID /
CHALK_API_SERVER in the environment or in ../.env.
"""

from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx
from dotenv import load_dotenv


# Skip VCS metadata and anything that tends to be huge + useless for opencode.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".ruff_cache", "dist", "build"}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10MB per file


def _get_access_token(api_server: str, client_id: str, client_secret: str) -> str:
    resp = httpx.post(
        f"{api_server.rstrip('/')}/v1/oauth/token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _rpc(api_server: str, headers: dict[str, str], method: str, body: dict) -> httpx.Response:
    return httpx.post(
        f"{api_server.rstrip('/')}/chalk.volume.v1.VolumeService/{method}",
        json=body,
        headers=headers,
        timeout=60,
    )


def _walk_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            print(f"  skip (too large): {p.relative_to(root)}", file=sys.stderr)
            continue
        out.append(p)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("git_url", help="Public git URL to clone")
    parser.add_argument("--volume", required=True, help="Target Chalk volume name")
    parser.add_argument("--branch", default=None, help="Optional branch to check out")
    args = parser.parse_args()

    for candidate in (".env", "../.env"):
        if os.path.exists(candidate):
            load_dotenv(candidate)
            break

    api_server = os.environ.get("CHALK_API_SERVER")
    client_id = os.environ.get("CHALK_CLIENT_ID")
    client_secret = os.environ.get("CHALK_CLIENT_SECRET")
    env_id = os.environ.get("CHALK_ENVIRONMENT_ID", "")
    if not (api_server and client_id and client_secret):
        sys.exit("CHALK_API_SERVER, CHALK_CLIENT_ID, CHALK_CLIENT_SECRET are required")

    token = _get_access_token(api_server, client_id, client_secret)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Chalk-Env-Id": env_id,
        "X-Chalk-Server": "go-api",
    }

    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = Path(tmp) / "repo"
        clone_cmd = ["git", "clone", "--depth", "1"]
        if args.branch:
            clone_cmd += ["--branch", args.branch]
        clone_cmd += [args.git_url, str(clone_dir)]
        print(f"Cloning {args.git_url} ...")
        subprocess.run(clone_cmd, check=True)

        # Idempotent create
        create_resp = _rpc(api_server, headers, "CreateVolume", {"name": args.volume})
        if create_resp.status_code not in (200, 409):
            sys.exit(f"CreateVolume failed: {create_resp.status_code} {create_resp.text}")

        files = _walk_files(clone_dir)
        print(f"Uploading {len(files)} files to volume '{args.volume}' ...")

        def _upload(path: Path) -> str:
            rel = str(path.relative_to(clone_dir))
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            resp = _rpc(api_server, headers, "PutFile", {
                "volumeName": args.volume, "path": rel, "data": data,
            })
            if resp.status_code != 200:
                raise RuntimeError(f"PutFile {rel}: {resp.status_code} {resp.text[:200]}")
            return rel

        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(_upload, f) for f in files]
            for i, fut in enumerate(as_completed(futures), 1):
                fut.result()
                if i % 50 == 0 or i == len(files):
                    print(f"  {i}/{len(files)}")

    print(f"\nDone. Volume '{args.volume}' is ready.")
    print(f"Next: uv run python opencode.py --volume {args.volume}")


if __name__ == "__main__":
    main()
