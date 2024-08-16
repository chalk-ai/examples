import json
from datetime import date

from chalk import DataFrame, FeatureTime, Windowed, _, feature, windowed
from chalk.features import features

default_completion = json.dumps(
    dict(
        category="unknown",
        is_nsf=False,
        is_ach=False,
        clean_memo="",
    )
)


@features
class Transaction:
    id: int
    amount: float
    memo: str

    # :tags: genai
    clean_memo: str

    # The User.id type defines our join key implicitly
    user_id: "User.id"
    user: "User"

    # The time at which the transaction was created for temporal consistency
    at: FeatureTime

    completion: str = feature(max_staleness="infinity", default=default_completion)

    category: str = "unknown"
    is_nsf: bool = False
    is_ach: bool = False


@features
class User:
    # Features pulled from Postgres for the user
    id: int
    email: str
    name: str
    dob: date

    # Whether the user appears in a denylist in s3
    denylisted: bool

    # The transactions, linked by the User.id type on the Transaction.user_id field
    transactions: DataFrame[Transaction]

    # The number of payments made by the user in the last 1, 7, and 30 days
    # Uses the category pulled from Gemini to count payments
    count_payments: Windowed[int] = windowed(
        "1d", "7d", "30d",
        expression=_.transactions[
            _.amount,
            _.at >= _.chalk_window,
            _.category == "payment"
        ].count(),
    )
