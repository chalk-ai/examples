"""An example of calcuating income from plaid transactions

In this example, we are using resolvers to compute User incomes based
on their plaid transactions.
"""

import re

from chalk import online
from chalk.features import features, DataFrame, has_many, after, FeatureTime
from datetime import datetime
import pytz

# Generally, implementing Chalk in your system requires three steps:
# 1. setting up features (these are pydantic inspired dataclasses that fully
# specify what you want your end data to look like),
# 2. setting up resolvers (these populate your features by pulling
# values directly from upstream raw data sources or by calling python
# functions on your upstream computed features).
# 3. setting up your upstream raw data sources.
#
# this example focuses on the first two steps and uses dummy resolvers
# with no upstream inputs to create mock data. This means it should be runnable
# in sandbox environments with a call to `chalk apply --branch credit` and
# no other configuration.


@features
class Transaction:
    id: int
    amount: float
    memo: str
    on: FeatureTime

    user_id: "User.id"
    user: "User"

    # Computed properties
    clean_memo: str
    is_payroll: bool


@features
class User:
    id: int
    self_reported_employer: str

    transactions: DataFrame[Transaction]

    # Computed properties
    computed_income_30: float


PAYROLL_SUBSTRINGS = {
    "des deposit",
    "dir dep",
    "direct dep",
    "directdep",
    "gusto",
    "payroll",
    "quickbooks",
    "redfin corp des",
    "rippling",
    "zenpayroll",
    "payroll",
}

MIN_PAYCHECK_SIZE = 400


@online
def get_clean_memo(memo: Transaction.memo) -> Transaction.clean_memo:
    computed = memo.lower()
    for prefix in ["sale", "pos", "tst", "sq"]:
        computed = computed.removeprefix(prefix).strip()
    return computed


@online
def get_transaction_payroll(
    memo_clean: Transaction.clean_memo,
    amount: Transaction.amount,
    employer: Transaction.user.self_reported_employer,
) -> Transaction.is_payroll:
    # Expenses in Plaid are greater than 0
    if amount > 0:
        return False

    # Too small and it's unlikely to really be payroll
    if -amount < MIN_PAYCHECK_SIZE:
        return False

    # If any of the standard payroll providers are in the memo, it's payroll
    if any(provider in memo_clean for provider in PAYROLL_SUBSTRINGS):
        return True

    employer_clean = (
        re.sub(
            pattern="[^a-z0-9]",
            repl=" ",
            string=employer.lower(),
        )
        .strip()
        .removesuffix("inc")
        .removesuffix("llc")
    )

    return employer_clean in memo_clean


@online
def get_plaid_income(
    txns: User.transactions[
        Transaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    """
    Each user has an associated set of transactions. This resolver filters a user's
    transactions based on the upstream computed `is_payroll` feature and selects
    only features from the previous 30 days.
    """
    return txns[Transaction.amount].sum()


# Below, we have a couple resolvers that generate basic test users and transactions.
# these resolvers allow this test code to be run without configuring any datasources.


@online
def get_test_plaid_users() -> DataFrame[User.id, User.self_reported_employer]:
    return DataFrame(
        [
            User(id=1, self_reported_employer="something inc."),
            User(id=2, self_reported_employer="Norms"),
        ]
    )


@online
def get_test_plaid_transactions() -> (
    DataFrame[Transaction.id, Transaction.user_id, Transaction.amount, Transaction.memo, Transaction.on]
):
    return DataFrame(
        [
            Transaction(id=1, user_id=1, amount=-277.0, memo="directdep", on=datetime(2014,8, 12)),
            Transaction(id=2, user_id=1, amount=-10_001, memo="other", on=datetime(2014,8, 12)),
            Transaction(id=3, user_id=1, amount=423.0, memo="test", on=datetime(2014,8, 12)),
            Transaction(id=4, user_id=1, amount=-1303.0, memo="paycheck", on=datetime(2014,8, 12)),
            Transaction(id=5, user_id=1, amount=124.0, memo="test", on=datetime(2014,8, 12)),
            Transaction(id=7, user_id=2, amount=2132.04, memo="undefined", on=datetime(2014,8, 12)),
            Transaction(id=6, user_id=2, amount=-1, memo="rippling", on=datetime(2014,8, 12)),
            Transaction(id=8, user_id=2, amount=-30, memo="payroll", on=datetime(2014,8, 12)),
            Transaction(id=9, user_id=2, amount=-999.99, memo="payroll", on=datetime(2014,8, 12)),
        ]
    )
