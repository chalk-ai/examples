from chalk.features import DataFrame, features


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


def get_transaction_total(
    txns: User.txns[Transaction.amount]
) -> User.txn_total:
    """we do not need the other fields in our transaction, so we can project, filtering out all columns except amount,
    making the sum operation more efficient
    """
    return txns.sum()
