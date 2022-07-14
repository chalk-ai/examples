import re

from datetime import datetime

from chalk import realtime
from chalk.features import features, feature_time, DataFrame, has_many, after, Features


@features
class PlaidTransaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: datetime = feature_time()

    # Computed properties
    clean_memo: str
    is_return: bool

    # Link back to the user
    user: "User"


@features
class User:
    id: str
    self_reported_income: int
    computed_income_30: float

    plaid_transactions: DataFrame[PlaidTransaction] = has_many(
        lambda: PlaidTransaction.user_id == User.id
    )


@realtime
def get_transaction_payroll(
    memo_clean: PlaidTransaction.clean_memo,
    amount: PlaidTransaction.amount,
    employer: PlaidTransaction.user.self_reported.employer,
) -> PlaidTransaction.is_return:
    ...


@realtime
def get_plaid_income(
    txns: User.plaid_transactions[
        PlaidTransaction.is_payroll == True,
        after(days_ago=30),
    ],
) -> Features[User.computed_income_30]:
    return -txns[PlaidTransaction.amount].sum()
