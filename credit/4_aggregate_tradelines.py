from chalk import realtime
from chalk.features import features, DataFrame, has_many


@features
class Tradeline:
    id: int
    user_id: int
    outstanding: float
    is_delinquent: bool


@features
class User:
    id: int
    delinquent_amount: float
    tradelines: DataFrame[Tradeline] = has_many(lambda: User.id == Tradeline.user_id)


@realtime
def tradeline_rollup(
    accounts: User.tradelines[
        Tradeline.is_delinquent is True
    ]
) -> User.delinquent_amount:
    """
    Sum the outstanding balances on tradelines that
    are marked as delinquent
    """
    return accounts[Tradeline.outstanding].sum()
