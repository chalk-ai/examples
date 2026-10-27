# Lock down an AI agent in a Chalk sandbox

A data-analysis agent answers questions about loan applications by writing and running Python.
The steps run it in a [Chalk sandbox](https://docs.chalk.ai/docs/compute/sandbox), then lock it
down one protection at a time:

| Step | Script | What changes |
| --- | --- | --- |
| 1 | `1_unrestricted.py` | The agent runs with no restrictions |
| 2 | `2_network.py` | The sandbox can reach only the Model Gateway |
| 3 | `3_key.py` | The sandbox holds a placeholder instead of the real gateway key |
| 4 | `4_limits.py` | The agent works on a snapshot of the data, with CPU, memory, and lifetime limits |
| 5 | `5_cleanup.py` | Deletes the data volume |

The walkthrough, with setup and the output of each step, is the
[tutorial in the Chalk docs](https://docs.chalk.ai/docs/sandboxes/agent-tutorial).

## Files

| File | Role |
| --- | --- |
| `config.py` | Your API host, environment ID, model, and the name of the secret that holds your gateway key |
| `agent.py` | The agent: a tool-calling loop that runs inside the sandbox |
| `common.py` | The sandbox image, the data volume, and the checks each step prints |
| `data/make_loans.py` | Generates `data/loans.csv`, 2,000 fictional loan applications |

## Quick start

```bash
chalk login
chalk router api-key create --description "Locked-down agent tutorial"
chalk secret set AGENT_GATEWAY_KEY      # paste the key from the previous command
# Edit config.py, then:
uv run 1_unrestricted.py
```
