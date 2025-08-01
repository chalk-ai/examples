from datetime import datetime
from chalk.features import features, DataFrame, _
from chalk import windowed, Windowed
import chalk.functions as F


@features
class User:
    id: int
    name: str
    created_at: datetime
    transactions: "DataFrame[Transaction]"

    # The amount of time since the user was created in seconds.
    time_since_creation: int = F.total_seconds(_.chalk_now - _.created_at)

    # The number of transactions the user has made in the last 1, 10, and 30 days.
    num_transactions: Windowed[int] = windowed(
        "1d",
        "10d",
        "30d",
        expression=_.transactions[_.ts < _.chalk_now, _.ts >= _.chalk_window].count(),
    )

    # The latest transaction timestamp for the user, considering only transactions
    latest_transaction_timestamp: datetime = _.transactions[
        _.ts, _.ts < _.chalk_now
    ].max()

    # The time since the last transaction in seconds.
    time_since_last_transaction: int = F.total_seconds(
        _.chalk_now - _.latest_transaction_timestamp
    )

    # The number of distinct merchants the user has transacted with in the last
    # 1, 10, and 30 days.
    num_distinct_merchants_transacted: Windowed[int] = windowed(
        "1d",
        "10d",
        "30d",
        expression=_.transactions[
            _.merchant_id, _.ts < _.chalk_now, _.ts >= _.chalk_window
        ].approx_count_distict(),
    )

    # The churn prediction is a float between 0 and 1, where 1 means the user is
    # predicted to churn.
    churn_prediction: float


@features
class Transaction:
    id: int
    amount: float
    merchant_id: int
    ts: datetime
    user_id: User.id
    user: User
    category: str

    # model score predicted by a scheduled job
    is_fraud: bool
