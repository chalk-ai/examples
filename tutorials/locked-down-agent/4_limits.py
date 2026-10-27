"""Step 4: give the agent a fixed snapshot of the data, and limit its resources and lifetime."""

import chalkcompute

import common
import config

volume = common.upload_data()
# A specific version of a volume is an immutable snapshot.
snapshot = volume.at_version(volume.latest_version().id)

sandbox = (
    chalkcompute.Sandbox(
        name="loan-agent",
        image=common.IMAGE,
        volumes=[snapshot.mount("/data")],
        env=common.AGENT_ENV,
        network_policy=chalkcompute.NetworkPolicy(allowed_hosts=[config.API_HOST]),
        cpu="1",
        memory="2Gi",
        lifetime="900s",  # Chalk terminates the sandbox after 15 minutes.
    )
    .add_credentials(config.API_HOST, config.KEY_SECRET)
    .run()
)

try:
    common.ask(sandbox, "Which loan purpose has the highest default rate?")
    common.check(
        sandbox,
        "Adding a row to /data/loans.csv inside the sandbox",
        "open('/data/loans.csv', 'a').write('A99999,car,1,1,1,1,0\\n'); print('done')",
    )
    common.check_internet(sandbox)
    common.check_key(sandbox)
finally:
    sandbox.terminate()

# The snapshot's changes stayed inside the sandbox. The saved data is unchanged.
saved = volume.read_file("loans.csv").decode()
print("Row A99999 in the saved data:", "A99999" in saved)
