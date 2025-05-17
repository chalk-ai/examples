from chalk.features import DataFrame, _, features
from chalk import online


@features
class Transaction:
    id: int
    user_id: "User.id"
    memo: str
    merchant: str
    amount: float


@features
class User:
    id: int
    txns: DataFrame[Transaction]
    txn_total: int


# Filters and projections can be combined
@online(tags=['v1'])
def get_transaction_total_v1(
    txns: User.txns[
        Transaction.amount < 0, # filter
        Transaction.amount      # projection
    ]
) -> User.txn_total:
    return txns.sum()


@online(tags=['v2'])
def get_transaction_total_v2(
    txns: User.txns[
        _.amount < 0,  # "_" is an alias for the current namespace
        _.amount
    ]
) -> User.txn_total:
    return txns.sum()
