import re
from datetime import datetime

from chalk import realtime
from chalk.features import features, feature_time, DataFrame, has_many, before, after, days_ago, years_ago


@features
class PlaidTransaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: datetime = feature_time()
    user: "User"



@features
class User:
    id: str
    plaid_transactions: DataFrame[PlaidTransaction] = has_many(
        lambda: PlaidTransaction.user_id == User.id
    )
    # percentage change last 30 days vs a year ago
    change_from_last_year: float



@realtime
def get_transaction_trend(this_year_txns: User.transactions[after(days_ago=30)],
                          last_year_txns: User.transactions[before(years_ago=1), after(years_ago=1, days_ago=30)]
                          ) -> User.change_from_last_year:
    sum_last = last_year_txns['amount'].sum()
    sum_this = this_year_txns['amount'].sum()
    return (sum_last - sum_this) * 100 / sum_last
    