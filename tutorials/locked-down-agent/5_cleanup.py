"""Step 5: delete the data volume. Each step already terminated its sandbox."""

import chalkcompute

import common

chalkcompute.Volume(common.VOLUME).delete()
print(f"Deleted volume {common.VOLUME}.")
