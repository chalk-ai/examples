import re
from datetime import datetime

from chalk import realtime
from chalk.features import features, feature_time, DataFrame, has_many


@features
class PlaidTransaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: datetime = feature_time()
    user: "User"

    # Computed properties
    is_nsf: bool

@features
class User:
    id: str
    nsf_amount: float
    plaid_transactions: DataFrame[PlaidTransaction] = has_many(
        lambda: PlaidTransaction.user_id == User.id
    )

@realtime
def get_clean_memo(memo: PlaidTransaction.memo) -> PlaidTransaction.clean_memo:
    computed = memo.lower()
    for prefix in ["sale", "pos", "tst", "sq"]:
        computed = computed.removeprefix(prefix).strip()
    return computed


@realtime
def get_transaction_is_nsf(
        memo_clean: PlaidTransaction.clean_memo,
) -> PlaidTransaction.is_nsf:
    return "nsf" in memo_clean.lower()

@realtime
def get_nsf_amount(amounts: User.plaid_transactions[
    PlaidTransaction.is_nsf is True,
    PlaidTransaction.amount]) -> User.nsf_amount:
    return amounts.sum()
    