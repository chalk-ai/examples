# Hello Chalk Compute

A minimal example that spins up a container using [Chalk Compute](https://chalk.ai), runs a few commands inside it, and tears it down.

## Quickstart

**1. Log in to Chalk**

```bash
chalk login
```

**2. Set credentials**

Export the following environment variables. You can find these values by running `chalk config` after logging in, or by creating an access token in the Chalk dashboard.

```bash
export CHALK_CLIENT_ID=...
export CHALK_CLIENT_SECRET=...
export CHALK_ENVIRONMENT_ID=...
export CHALK_API_SERVER=...
```

**3. Run the example**

```bash
uv run hello.py
```

This will:
- Pull a Python 3.12 slim image and install `cowsay`
- Start a container with a volume mounted at `/data`
- Run `uname`, `python --version`, and a `cowsay` greeting inside the container
- Stop and clean up the container
