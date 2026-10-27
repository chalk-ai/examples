"""A small data-analysis agent. It runs inside the sandbox.

The agent answers a question about /data/loans.csv by asking a model to write Python, running that
Python, and sending the output back to the model until the model gives an answer. The model is
reached through the Chalk Model Gateway with an OpenAI-compatible client.

Usage: python agent.py "your question"
"""

import json
import os
import subprocess
import sys

from openai import OpenAI

SYSTEM_PROMPT = """You are a data analyst. Answer the user's question about loan applications by
writing Python that reads /data/loans.csv with pandas. Use the run_python tool to run it, and
always print() the values you need to see. The file has these columns:

application_id, purpose, loan_amount, annual_income, credit_score, term_months, defaulted

`defaulted` is 1 if the loan defaulted and 0 if it did not. When you have the answer, reply with
a short explanation that includes the numbers you found."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Run a Python script and return what it printed.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "description": "The Python script."}},
                "required": ["code"],
            },
        },
    }
]


def run_python(code: str) -> str:
    """Run code in a separate process and return its output, or say clearly that there was none."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        return "The script ran for more than 60 seconds and was stopped."
    output = (result.stdout + result.stderr).strip()
    if not output:
        return "The script ran without printing anything. Use print() to see values."
    return output[-4000:]


def main() -> None:
    question = sys.argv[1]
    client = OpenAI(
        base_url=f"https://{os.environ['API_HOST']}/v1/router",
        api_key=os.environ[os.environ["KEY_SECRET"]],
        default_headers={"X-Chalk-Env-Id": os.environ["ENVIRONMENT_ID"]},
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for _ in range(8):
        response = client.chat.completions.create(
            model=os.environ["MODEL"], messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        messages.append(message)
        if not message.tool_calls:
            print(f"\nAnswer: {message.content}")
            return
        for call in message.tool_calls:
            code = json.loads(call.function.arguments)["code"]
            output = run_python(code)
            print(f"--- ran {len(code.splitlines())} lines of Python")
            print(output[:500])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
    print("\nThe agent stopped after 8 turns without an answer.")


if __name__ == "__main__":
    main()
