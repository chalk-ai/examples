from time import sleep

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.sensors.base import PokeReturnValue

from chalk.client import ChalkClient


@dag(
    schedule=None,
    start_date=pendulum.datetime(2024, 5, 7, tz="UTC"),
    catchup=False,
    tags=["chalk"],
)
def taskflow_with_chalk():
    """
    Simple example of setting up airflow DAG that triggers Chalk resolvers
    """

    @task()
    def extract(): ...

    @task(multiple_outputs=True)
    def transform(): ...

    @task()
    def load(): ...

    @task.virtualenv(
        task_id="virtualenv_python",
        requirements=["chalkpy"],
        system_site_packages=False,
    )
    def run_chalk_resolver_virtual_env():
        """
        Trigger the resolver.get_email_domain resolver in a virtual environment
        """
        from chalk.client import ChalkClient

        # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
        # are passed to airflow.
        client = ChalkClient()

        result = client.trigger_resolver_run(
            "get_users"  # this is the name of our sql file resolver {name}.chalk.sql
        )
        if result.status == "failed":
            raise AirflowFailException(f"Resolver run failed: {result}")
        return result.id

    @task()
    def run_chalk_resolver() -> str:
        """
        Trigger the resolver.get_email_domain resolver
        """

        # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
        # are passed to airflow.
        client = ChalkClient()

        result = client.trigger_resolver_run(
            "get_users"  # this is the name of our sql file resolver {name}.chalk.sql
        )
        if result.status == "failed":
            raise AirflowFailException(f"Resolver run failed: {result}")
        return result.id

    @task.sensor(poke_interval=30, timeout=60 * 5)
    def poll_resolver_run(run_id) -> PokeReturnValue:
        """
        Poll the running chalk resolver
        """

        # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
        # are passed to airflow.
        client = ChalkClient()

        if (status := client.get_run_status(run_id).status) == "succeeded":
            if status == "succeeded":
                return PokeReturnValue(True, run_id)
            elif status == "failed":
                raise AirflowFailException(f"Chalk resolver resolver run: {run_id}")
        return PokeReturnValue(False)

    extract()
    transform()
    load()
    rid = run_chalk_resolver()
    poll_resolver_run(rid)
    # run_chalk_resolver_virtual_env()


taskflow_with_chalk()
