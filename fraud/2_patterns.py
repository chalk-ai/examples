from chalk import online
from chalk.features import features, DataFrame, has_many, before, after, FeatureTime


@features
class PlaidTransaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: FeatureTime
    user: "User"


@features
class User:
    id: PlaidTransaction.user_id
    plaid_transactions: DataFrame[PlaidTransaction]

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
    sum_last = last_year_txns[PlaidTransaction.amount].sum()
    sum_this = this_year_txns[PlaidTransaction.amount].sum()
    return (sum_last - sum_this) * 100 / sum_last
