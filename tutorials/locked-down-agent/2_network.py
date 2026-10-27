"""Step 2: allow the sandbox to reach only the Model Gateway."""

import chalkcompute

import common
import config

common.upload_data()

sandbox = chalkcompute.Sandbox(
    name="loan-agent",
    image=common.IMAGE,
    volumes=[(common.VOLUME, "/data")],
    env={
        **common.AGENT_ENV,
        config.KEY_SECRET: chalkcompute.Secret.from_chalk_env(config.KEY_SECRET),
    },
    # Every other host is blocked.
    network_policy=chalkcompute.NetworkPolicy(allowed_hosts=[config.API_HOST]),
).run()

try:
    common.ask(sandbox, "Which loan purpose has the highest default rate?")
    common.check_internet(sandbox)
    common.check_key(sandbox)
finally:
    sandbox.terminate()
