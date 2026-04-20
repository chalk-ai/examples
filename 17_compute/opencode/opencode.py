#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.11"
# dependencies = ["chalkcompute>=1.1.1", "python-dotenv"]
# ///

# # OpenCode on a Chalk volume
#
# Launch an [OpenCode](https://opencode.ai) server inside a Chalk container,
# with a source tree pre-loaded from a persistent Chalk volume. The volume
# must already exist — populate it first with:
#
#     uv run python populate_volume.py <git-url> --volume <name>
#
# Then run this example, pointing at the same volume name:
#
#     uv run python opencode.py --volume <name>
#
# The container mounts the volume at `/root/code` so OpenCode opens directly
# into the repo — no git clone at container startup.
#
# ## Environment variables
#
#     CHALK_CLIENT_ID/SECRET    Required for the SDK + ChalkFS volume mount.
#     OPENCODE_SERVER_PASSWORD  Optional password for the server.
#     ANTHROPIC_API_KEY         Forwarded into the container.
#     OPENAI_API_KEY            Forwarded into the container.

import argparse
import logging
import os
import time
import uuid

from chalkcompute import Container, Image
from dotenv import load_dotenv

for _candidate in (".env", "../.env"):
    if os.path.exists(_candidate):
        load_dotenv(_candidate)
        break

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

OPENCODE_PORT = 4096
OPENCODE_BIN = "/root/.opencode/bin/opencode"
MOUNT_PATH = "/root/code"

# ## Image — Go toolchain + opencode
#
# We start from a Go image so the LSP and build tools work out of the box,
# then layer on curl + opencode. Swap the base image if you're editing a
# different language stack.

OPENCODE_IMAGE = (
    Image.base("golang:1.24-bookworm")
    .run_commands(
        "apt-get update -qq && apt-get install -y -qq curl git 2>&1",
        "curl -fsSL https://opencode.ai/install | bash 2>&1",
    )
)


def start_server(container: Container) -> None:
    """Kill the placeholder HTTP server and start opencode serve."""
    log.info("Stopping placeholder HTTP server on port %d...", OPENCODE_PORT)
    container.exec(
        "bash", "-c",
        "kill $(cat /tmp/http_server.pid 2>/dev/null) 2>/dev/null; "
        "rm -f /tmp/http_server.pid; true",
    )

    log.info("Starting opencode server on port %d...", OPENCODE_PORT)
    # Write a launcher script so the exec returns immediately
    container.exec(
        "bash", "-c",
        "cat > /tmp/start_opencode.sh << 'SCRIPT'\n"
        "#!/bin/bash\n"
        f"cd {MOUNT_PATH}\n"
        f"exec {OPENCODE_BIN} serve --hostname=0.0.0.0 --port={OPENCODE_PORT} --log-level=DEBUG\n"
        "SCRIPT\n"
        "chmod +x /tmp/start_opencode.sh",
        timeout_secs=10,
    )
    container.exec(
        "bash", "-c",
        "nohup /tmp/start_opencode.sh > /tmp/opencode.log 2>&1 &",
        timeout_secs=10,
    )

    log.info("Waiting for opencode to be ready...")
    for attempt in range(60):
        result = container.exec(
            "bash", "-c",
            f"curl -s http://localhost:{OPENCODE_PORT} > /dev/null 2>&1; echo $?",
            timeout_secs=10,
        )
        if result.stdout_text.strip() == "0":
            return
        if attempt < 59:
            time.sleep(2)
    raise RuntimeError(
        "opencode server did not become ready after 2 minutes.\n"
        "Check /tmp/opencode.log inside the container for details."
    )


def main(
    container_name: str,
    password: str | None,
    timeout_secs: int,
    volume_name: str,
) -> None:
    env: dict[str, str] = {}
    if password:
        env["OPENCODE_SERVER_PASSWORD"] = password
    if anthropic_key := os.environ.get("ANTHROPIC_API_KEY"):
        env["ANTHROPIC_API_KEY"] = anthropic_key
    if openai_key := os.environ.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = openai_key
    # ChalkFS needs credentials to mount the volume
    if client_id := os.environ.get("CHALK_CLIENT_ID"):
        env["CHALK_CLIENT_ID"] = client_id
    if client_secret := os.environ.get("CHALK_CLIENT_SECRET"):
        env["CHALK_CLIENT_SECRET"] = client_secret

    container = Container(
        image=OPENCODE_IMAGE,
        name=container_name,
        env=env,
        port=OPENCODE_PORT,
        volumes=[(volume_name, MOUNT_PATH)],
        entrypoint=[
            "bash", "-c",
            f"python3 -m http.server {OPENCODE_PORT} --bind 0.0.0.0 "
            f"&>/dev/null & echo $! > /tmp/http_server.pid; tail -f /dev/null",
        ],
    ).run()

    # Don't let stop() delete the persistent shared volume
    container._volumes = []

    try:
        # Verify volume is mounted
        result = container.exec("ls", MOUNT_PATH)
        log.info("Volume contents: %s", result.stdout_text.strip()[:200])

        start_server(container)

        container.refresh()
        web_url = container.info.web_url if container.info else None
        log.info("--- OpenCode server ready (%s) ---", volume_name)
        if web_url:
            log.info("  Web UI:  %s", web_url)
            pw_prefix = f"OPENCODE_SERVER_PASSWORD={password} " if password else ""
            log.info("  TUI:     %sopencode attach %s", pw_prefix, web_url)
        else:
            log.info("  Container ID: %s", container.id)
        log.info("----------------------------------------")

        mins = timeout_secs // 60
        log.info("Server running. Press Ctrl-C to stop (timeout: %dm).", mins)
        time.sleep(timeout_secs)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        container.stop()
        log.info("Container stopped.")


def _parse_timeout(value: str) -> int:
    if value.endswith("h"):
        return int(value[:-1]) * 3600
    if value.endswith("m"):
        return int(value[:-1]) * 60
    return int(value) * 3600


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Launch OpenCode in a Chalk container backed by a Chalk volume",
    )
    parser.add_argument(
        "--volume", type=str, required=True,
        help="Name of an existing Chalk volume (populate with populate_volume.py first)",
    )
    parser.add_argument(
        "--timeout", type=str, default="12",
        help="Server lifetime (e.g. 2h, 90m). Bare number = hours. Default: 12",
    )
    parser.add_argument(
        "--name", type=str,
        default=f"opencode-{uuid.uuid4().hex[:8]}",
        help="Container name",
    )
    parser.add_argument(
        "--password", type=str,
        default=os.environ.get("OPENCODE_SERVER_PASSWORD"),
        help="OpenCode server password",
    )
    args = parser.parse_args()
    main(
        container_name=args.name,
        password=args.password,
        timeout_secs=_parse_timeout(args.timeout),
        volume_name=args.volume,
    )
