from airflow.decorators import task
from airflow.exceptions import AirflowFailException


@task.virtualenv(
    task_id="virtualenv_python", requirements=["chalkpy"], system_site_packages=False
)
def run_chalk_resolver() -> str:
    """
    Trigger the resolver.get_email_domain resolver in a virtual environment
    """
    from chalk.client import ChalkClient

    # This assumes that CHALK_CLIENT_SECRET, CHALK_CLIENT_ID, & CHALK_ENVIRONMENT  environment variables
    # are passed to airflow.
    client = ChalkClient()

    result = client.trigger_resolver_run(
        "get_users"
    )
    if result.status == "failed":
        raise AirflowFailException(f"Resolver run failed: {result}")
    return result.id