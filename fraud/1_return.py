"""An example of calculating non-sufficient fund (NSF) amount from
a user's transactions
"""

from chalk import online
from chalk.features import features, DataFrame, FeatureTime

from datetime import datetime
import pytz


@features
class Transaction:
    id: str
    amount: float
    memo: str
    on: FeatureTime
    user_id: "User.id"
    user: "User"

    # Computed properties
    clean_memo: str
    is_nsf: bool # non-sufficient funds


@features
class User:
    id: int
    transactions: DataFrame[Transaction]

    # Computed properties
    nsf_amount: float


@online
def get_clean_memo(memo: Transaction.memo) -> Transaction.clean_memo:
    computed = memo.lower()
    for prefix in ("sale", "pos", "tst", "sq"):
        computed = computed.removeprefix(prefix).strip()
    return computed


@online
def get_transaction_is_nsf(
    memo_clean: Transaction.clean_memo,
) -> Transaction.is_nsf:
    return "nsf" in memo_clean.lower()


@online
def get_nsf_amount(amounts: User.transactions[Transaction.is_nsf is True, Transaction.amount]) -> User.nsf_amount:
    """
    In this resolver, we calculate the total NSF ammount for our users.
    """
    return amounts.sum()


# Below we generate a couple dummy resolvers to make the example fully runnable without connected
# datasources.


@online
def get_test_users() -> DataFrame[User.id]:
    return DataFrame([
        User(id=1),
        User(id=2),
    ])


@online
def get_test_transactions() -> (
    DataFrame[Transaction.id, Transaction.user_id, Transaction.amount, Transaction.memo, Transaction.on]
):
    return DataFrame([
        Transaction(id=1, user_id=1, amount=-277.0, memo="directdep", on=datetime(2014, 8, 12)),
        Transaction(id=2, user_id=1, amount=-10_001.0, memo="other", on=datetime(2014, 8, 12)),
        Transaction(id=3, user_id=1, amount=42.1, memo="tetst nsf", on=datetime(2014,8, 12)),
        Transaction(id=4, user_id=1, amount=-1303.0, memo="paycheck", on=datetime(2014,8, 12)),
        Transaction(id=5, user_id=1, amount=124.0, memo="test", on=datetime(2014,8, 12)),
        Transaction(id=7, user_id=2, amount=2132.04, memo="undefined", on=datetime(2014,8, 12)),
        Transaction(id=6, user_id=2, amount=-1.0, memo="sale nsf", on=datetime(2014,8, 12)),
        Transaction(id=8, user_id=2, amount=-30.0, memo="tst nsf", on=datetime(2014,8, 12)),
        Transaction(id=9, user_id=2, amount=-999.99, memo="payroll", on=datetime(2014,8, 12)),
    ])
