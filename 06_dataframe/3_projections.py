from chalk.features import features, DataFrame


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


# You can filter down the transactions by any of the
# properties on the transaction
credits = User.txns[Transaction.amount]
