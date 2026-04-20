import json
import sys

import chalkcompute

agent = chalkcompute.RemoteFunction.from_name(name="fraud-agent")
agent.wait_ready()

transaction_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
verdict_json = agent(transaction_id)
print(json.dumps(json.loads(verdict_json), indent=2))
