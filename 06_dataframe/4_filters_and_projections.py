from chalk.features import features, DataFrame, _


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
credits = User.txns[Transaction.amount < 0]

# You can also use the '_' as an alias for the current namespace
credits = User.txns[_.amount < 0]
