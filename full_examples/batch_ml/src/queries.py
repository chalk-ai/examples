from chalk import ScheduledQuery, NamedQuery
from src.models import Transaction


# Scheduled Queries allow you to compute a specified
# set of features on a schedule, useful for persisting
# values to the online and offline stores.
# https://docs.chalk.ai/docs/scheduled-query

sq = ScheduledQuery(
    name="run_fraud_model",
    schedule="0 0 * * *",  # Every day at midnight
    output=[
        Transaction.is_fraud,
    ],
    store_online=True,
    store_offline=True,
    tags=["model_sample"],
    incremental_resolvers=["get_transactions_offline"],
)
