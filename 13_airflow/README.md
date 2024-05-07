# Chalk Resolvers Can Be Triggered

It's really easy to trigger a Chalk resolver as part of an airflow workflow: just add some environment
variables, some python dependencies, and create a new resolver task.

## Setup

To run chalk resolver's in airflow, you'll need to add `CHALK_CLIENT_ID` and `CHALK_CLIENT_SECRET` to your 
airflow environment variables. With this done, you'll be able to create a ChalkClient instance in an
airflow task and trigger a resolver run.

The task can either use a shared python environment or an isolated python environment.

If you want to create a specific access token for airflow, this can be done in the settings -> Access Tokens 
page of the chalk dashboard:
![access_token](./airflow.png)


## Shared Python Environment

If you plan to use a shared python environment, you need to add the `chalkpy` package to your
set of airflow dependencies.

```python
from airflow.decorators import task
from chalk.client import ChalkClient

@task
def run_chalk_resolver():
    """
    Trigger the resolver.get_email_domain resolver in a virtual environment
    """

    # This assumes that CHALK_CLIENT_SECRET & CHALK_CLIENT_ID environment variables
    # are passed to airflow.
    client = ChalkClient()

    client.trigger_resolver_run(
        "resolver.get_email_domain"
    )
```

## Isolated Python Environment

To isolate the Chalk operator from your python environment, you can use airflow's `@task.virtualenv` decorator:

```python
from airflow.decorators import task

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
```
