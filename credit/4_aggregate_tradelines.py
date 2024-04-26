"""An example of connecting Users to Tradelines.

In particular, this example show how to filter
transactions in a resolver for a computed feature.
"""
from chalk import online
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


@online
def tradeline_rollup(
    accounts: User.tradelines[
        # resolvers can request a subset of a DataFrame's rows as input
        # (https://docs.chalk.ai/docs/dataframe#filters).
        Tradeline.is_delinquent is True
    ]
    ) -> User.delinquent_amount:
    """
    Sum the outstanding balances on tradelines that
    are marked as delinquent.
    """
    return accounts[Tradeline.outstanding].sum()
