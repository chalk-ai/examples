"""Step 3: keep the real gateway key out of the sandbox."""

import chalkcompute

import common
import config

common.upload_data()

sandbox = (
    chalkcompute.Sandbox(
        name="loan-agent",
        image=common.IMAGE,
        volumes=[(common.VOLUME, "/data")],
        env=common.AGENT_ENV,
        network_policy=chalkcompute.NetworkPolicy(allowed_hosts=[config.API_HOST]),
    )
    # The sandbox gets a placeholder. Chalk swaps in the real key on requests to the gateway host.
    .add_credentials(config.API_HOST, config.KEY_SECRET)
    .run()
)

try:
    common.ask(sandbox, "Which loan purpose has the highest default rate?")
    common.check_internet(sandbox)
    common.check_key(sandbox)
finally:
    sandbox.terminate()
