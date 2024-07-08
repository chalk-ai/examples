from datetime import datetime

from chalk import online
from chalk.features import DataFrame, features


@features
class Transaction:
    id: int
    user_id: "User.id"
    memo: str
    merchant: str
    amount: float
    canceled_at: None | datetime


@features
class User:
    id: int
    txns: DataFrame[Transaction]

    # Computed Fields

    num_valid_txns: int
    num_rideshare_txns: int


# You can filter down the transactions by any of the properties on the transaction


@online(tags=["v1"])
def get_count_rideshare_transactions_v1(
    txns: User.txns[Transaction.merchant in ("uber", "lyft")]
) -> User.num_rideshare_txns:
    # You can also check for set or list membership with `in`:
    return len(txns)


@online(tags=["v2"])
def get_count_rideshare_transactions_v2(
    txns: User.txns[Transaction.amount < 0, Transaction.merchant in ("uber", "lyft")]
) -> User.num_rideshare_txns:
    # Filters separated by commas function as `and` filters:
    return len(txns)


@online(tags=["v3"])
def get_count_rideshare_transactions_v3(
    txns: User.txns[Transaction.amount < 0 and Transaction.merchant in ("uber", "lyft")]
) -> User.num_rideshare_txns:
    # Equivalently, you can use the keyword `and` instead of separating by commas to apply multiple filters.
    return len(txns)


@online(tags=["v4"])
def get_count_rideshare_transactions_v4(
    txns: User.txns[
        Transaction.amount < 0
        and (Transaction.merchant in ("uber", "lyft") or "uberpmts" == Transaction.memo)
    ]
) -> User.num_rideshare_txns:
    # or filters can also be applied through the "or" keyword
    return len(txns)


@online
def get_count_valid_transactions(
    valid_transactions: User.txns[Transaction.canceled_at is not None],
) -> User.num_valid_transactions:
    # Filters can also check for None the same way you check for None in Python
    return len(valid_transactions)
