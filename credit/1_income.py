import re

from chalk import realtime
from chalk.features import features, DataFrame, has_many, after, FeatureTime


@features
class Transaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: FeatureTime
    user: "User"

    # Computed properties
    clean_memo: str
    is_payroll: bool


@features
class User:
    id: str
    self_reported_employer: str
    computed_income_30: float
    transactions: DataFrame[Transaction] = has_many(lambda: Transaction.user_id == User.id)


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
def get_clean_memo(memo: Transaction.memo) -> Transaction.clean_memo:
    computed = memo.lower()
    for prefix in ["sale", "pos", "tst", "sq"]:
        computed = computed.removeprefix(prefix).strip()
    return computed


@realtime
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


@realtime
def get_plaid_income(
    txns: User.transactions[
        Transaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    return -txns[Transaction.amount].sum()
