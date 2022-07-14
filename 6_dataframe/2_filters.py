from datetime import datetime

from chalk.features import features

from features import DataFrame


@features
class Transaction:
    id: int
    memo: str
    merchant: str
    amount: float
    canceled_at: None | datetime


@features
class User:
    id: int
    txns: DataFrame[Transaction]


# You can filter down the transactions by any of the
# properties on the transaction
credits = User.txns[Transaction.amount < 0]

# You can also check for set or list membership with `in`:
rideshare_txns = User.txns[Transaction.merchant in {"uber", "lyft"}]

# Filters separated by commas function as `and` filters:
rideshare_credits = User.txns[
    Transaction.amount < 0, Transaction.merchant in {"uber", "lyft"}
]

# Equivalently, you can use the keyword `and` instead of separating by commas
rideshare_credits = User.txns[
    Transaction.amount < 0 and Transaction.merchant in {"uber", "lyft"}
]

# Or works much like `and`:
rideshare_income = User.txns[
    Transaction.amount < 0
    and (Transaction.merchant in {"uber", "lyft"} or "uberpmts" in Transaction.memo)
]

# Filters can also check for None the same way you check for None in Python
valid_txns = User.txns[Transaction.canceled_at is not None]
