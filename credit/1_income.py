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
    user: "User"

    # Computed properties
    clean_memo: str
    is_payroll: bool


@features
class User:
    id: str
    self_reported_employer: str
    computed_income_30: float
    plaid_transactions: DataFrame[PlaidTransaction] = has_many(
        lambda: PlaidTransaction.user_id == User.id
    )


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


@realtime
def get_clean_memo(memo: PlaidTransaction.memo) -> PlaidTransaction.clean_memo:
    computed = memo.lower()
    for prefix in ["sale", "pos", "tst", "sq"]:
        computed = computed.removeprefix(prefix).strip()
    return computed


@realtime
def get_transaction_payroll(
    memo_clean: PlaidTransaction.clean_memo,
    amount: PlaidTransaction.amount,
    employer: PlaidTransaction.user.self_reported_employer,
) -> PlaidTransaction.is_payroll:
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


@realtime
def get_plaid_income(
    txns: User.plaid_transactions[
        PlaidTransaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    return -txns[PlaidTransaction.amount].sum()
