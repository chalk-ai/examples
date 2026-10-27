"""Pieces every step shares: the sandbox image, the data volume, and how to run the agent."""

from pathlib import Path

import chalkcompute

import config

HERE = Path(__file__).parent
VOLUME = "loan-agent-data"

# The image has Python, pandas, and the OpenAI client installed, plus the agent script.
# Packages are installed while the image builds, before any network policy applies.
IMAGE = (
    chalkcompute.Image.debian_slim("3.12")
    .pip_install(["openai", "pandas"])
    .add_local_file(str(HERE / "agent.py"), "/app/agent.py")
)

# Settings the agent reads from its environment. None of them is secret.
AGENT_ENV = {
    "API_HOST": config.API_HOST,
    "ENVIRONMENT_ID": config.ENVIRONMENT_ID,
    "MODEL": config.MODEL,
    "KEY_SECRET": config.KEY_SECRET,
}


def upload_data() -> chalkcompute.Volume:
    """Upload data/loans.csv to the volume, creating the volume the first time."""
    volume = chalkcompute.Volume(VOLUME)
    volume.put_file("loans.csv", (HERE / "data" / "loans.csv").read_bytes())
    return volume


def check(sandbox: chalkcompute.Sandbox, description: str, code: str) -> None:
    """Run a short Python check inside the sandbox and print its result."""
    result = sandbox.exec("python", "-c", code, timeout_secs=60)
    print(f"{description}: {(result.stdout_text + result.stderr_text).strip()}")


def check_key(sandbox: chalkcompute.Sandbox) -> None:
    """Report whether the sandbox holds the real gateway key or a placeholder, without printing the key."""
    check(
        sandbox,
        "Key inside the sandbox",
        f"import os; k = os.environ['{config.KEY_SECRET}']; "
        "print('a placeholder: ' + k if k.startswith('__chalk-secret') "
        "else f'the real key ({len(k)} characters)')",
    )


def check_internet(sandbox: chalkcompute.Sandbox) -> None:
    """Try to reach a site outside the allowlist."""
    check(
        sandbox,
        "Request to pypi.org",
        "import urllib.request\n"
        "try:\n"
        "    print(urllib.request.urlopen('https://pypi.org/simple/', timeout=15).status)\n"
        "except Exception as e:\n"
        "    print(type(e).__name__, e)",
    )


def ask(sandbox: chalkcompute.Sandbox, question: str) -> None:
    """Run the agent in the sandbox and print what it does."""
    print(f"Question: {question}\n")
    result = sandbox.exec("python", "/app/agent.py", question, timeout_secs=300)
    print(result.stdout_text)
    if result.stderr_text.strip():
        print(result.stderr_text[-2000:])
