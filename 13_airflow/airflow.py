import os

from airflow.decorators import dag, task
import pendulum


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
    def extract():
        ...

    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        ...

    @task()
    def load(order_data_dict: dict):
        ...

    @task.virtualenv(
        task_id="virtualenv_python", requirements=["chalkpy"], system_site_packages=False
    )
    def run_chalk_resolver():
        """
        Trigger the resolver.get_email_domain resolver in a virtual environment
        """
        from chalk.client import ChalkClient

        # This assumes that CHALK_CLIENT_SECRET & CHALK_CLIENT_ID environment variables
        # are passed to airflow.
        client = ChalkClient()

        client.trigger_resolver_run(
            "resolver.get_email_domain"
        )

    @task.docker(
        image="chalk-ai:base",
        environment={
            "CHALK_CLIENT_SECRET": os.environ.get("CHALK_CLIENT_SECRET"),
            "CHALK_CLIENT_ID": os.environ.get("CHALK_CLIENT_ID")
        }
    )
    def run_chalk_resolver():
        """
        Trigger the resolver.get_email_domain resolver in a chalk docker container environment
        """
        from chalk.client import ChalkClient
        import os

        # This assumes that CHALK_CLIENT_SECRET & CHALK_CLIENT_ID environment variables
        # are configured for the airflow.

        client = ChalkClient()

        client.trigger_resolver_run(
            "resolver.get_email_domain"
        )

    extract()
    transform()
    load()
    run_chalk_resolver()


taskflow_with_chalk()
