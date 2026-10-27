"""Step 1: run the agent in a sandbox with no restrictions."""

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
        # The real gateway key, as an environment variable the agent can read.
        config.KEY_SECRET: chalkcompute.Secret.from_chalk_env(config.KEY_SECRET),
    },
).run()

try:
    common.ask(sandbox, "Which loan purpose has the highest default rate?")
    common.check_internet(sandbox)
    common.check_key(sandbox)
finally:
    sandbox.terminate()
