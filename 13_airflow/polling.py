from airflow.decorators import task
from airflow.sensors.base import PokeReturnValue
from chalk.client import ChalkClient
from airflow.exceptions import AirflowFailException


@task.sensor(poke_interval=30, timeout=60 * 5)
def poll_resolver_run(run_id) -> PokeReturnValue:
    """
    Poll the running chalk resolver
    """
    # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
    # are passed to airflow.
    client = ChalkClient()
    status = client.get_run_status(run_id).status

    if status == "succeeded":
        return PokeReturnValue(True, run_id)
    elif status == "failed":
        raise AirflowFailException(f"Chalk resolver resolver run: {run_id}")
    return PokeReturnValue(False)