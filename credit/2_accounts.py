from datetime import datetime

from chalk import realtime
from chalk.features import features, DataFrame, has_many, FeatureTime
from chalk.sql import PostgreSQLSource


@features
class Account:
    id: int
    bank_account_number: int
    decision: str
    user_id: str
    created_at: datetime
    # https://docs.chalk.ai/docs/features#feature-time
    updated_at: FeatureTime


# Bank accounts are stored in SQL.
# Credentials are stored as Chalk secrets
pg = PostgreSQLSource(name="CLOUD_DB").with_table(name="accounts", features=Account)


@features
class User:
    id: str
    name: str
    number_of_accounts: int
    accounts: DataFrame[Account] = has_many(lambda: Account.user_id == User.id)


@realtime
def count_accounts(accounts: User.accounts) -> User.number_of_accounts:
    return len(accounts)
