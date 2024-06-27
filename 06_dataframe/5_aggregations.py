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
    num_credits: int


# You can filter down the transactions by any of the
# properties on the transaction
@online
def get_num_credits(credits: User.txns[Transaction.amount < 0]) -> User.num_credits:
    return len(credits)
