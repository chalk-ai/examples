"""An example of calculating non-sufficient fund (NSF) amount from
a user's transactions
"""

from chalk import online
from chalk.features import features, DataFrame, before, after, FeatureTime


@features
class Transaction:
    id: int
    amount: float
    memo: str
    on: FeatureTime
    user_id: "User.id"
    user: "User"


@features
class User:
    id: int
    plaid_transactions: DataFrame[Transaction]

    # percentage change last 30 days vs a year ago
    change_from_last_year: float


@online
def get_transaction_trend(
    this_year_txns: User.transactions[after(days_ago=30)],
    last_year_txns: User.transactions[before(days_ago=30), after(days_ago=2*30)],
) -> User.change_from_last_year:
    """
    Calculates the percentage change in total transaction amount between
    30 day windows.
    """
    sum_last = last_year_txns[Transaction.amount].sum()
    sum_this = this_year_txns[Transaction.amount].sum()
    return (sum_last - sum_this) * 100 / sum_last
