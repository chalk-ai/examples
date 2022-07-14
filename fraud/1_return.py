from chalk import realtime
from chalk.features import features, DataFrame, has_many, FeatureTime


@features
class Transaction:
    id: str
    user_id: str
    amount: float
    memo: str
    on: FeatureTime
    user: "User"

    # Computed properties
    is_nsf: bool


@features
class User:
    id: str
    nsf_amount: float
    transactions: DataFrame[Transaction] = has_many(lambda: Transaction.user_id == User.id)


@realtime
def get_clean_memo(memo: Transaction.memo) -> Transaction.clean_memo:
    computed = memo.lower()
    for prefix in ("sale", "pos", "tst", "sq"):
        computed = computed.removeprefix(prefix).strip()
    return computed


@realtime
def get_transaction_is_nsf(
    memo_clean: Transaction.clean_memo,
) -> Transaction.is_nsf:
    return "nsf" in memo_clean.lower()


@realtime
def get_nsf_amount(amounts: User.transactions[Transaction.is_nsf is True, Transaction.amount]) -> User.nsf_amount:
    return amounts.sum()
