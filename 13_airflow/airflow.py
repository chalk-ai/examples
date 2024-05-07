
from airflow.decorators import dag, task
import pendulum
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
    def run_chalk_resolver_virtual_env():
        """
        Trigger the resolver.get_email_domain resolver in a virtual environment
        """
        from chalk.client import ChalkClient

        # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
        # are passed to airflow.
        client = ChalkClient()

        client.trigger_resolver_run(
            "get_users" # this is the name of our sql file resolver {name}.chalk.sql
        )

    @task
    def run_chalk_resolver():
        """
        Trigger the resolver.get_email_domain resolver
        """

        # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT environment variables
        # are passed to airflow.
        client = ChalkClient()

        client.trigger_resolver_run(
            "get_users" # this is the name of our sql file resolver {name}.chalk.sql
        )

    extract()
    transform()
    load()
    run_chalk_resolver()
    # run_chalk_resolver_virtual_env()


taskflow_with_chalk()
