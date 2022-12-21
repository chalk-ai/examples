from datetime import datetime
from chalk import realtime
from chalk.features import features, feature_time, DataFrame, has_many
from chalk.sql import MySQLSource

@features
class BankAccount:
    bank_account_number     : int
    decision                : str
    userName                : str
    created_at              : datetime
    # https://docs.chalk.ai/docs/features#feature-time
    updated_at              : datetime = feature_time()

# Bank accounts are stored in sql
# credentials are stored as chalk secrets
mysql = MySQLSource(name="CLOUD_DB")
mysql.with_table(name="accounts", features=BankAccount)

@features
class User:
    id                 : str
    name               : str
    accounts           : DataFrame[BankAccount] \
        = has_many(lambda: BankAccount.userName == User.name)
    number_of_accounts : int

@realtime
def count_accounts(accounts: User.accounts
) -> User.number_of_accounts:
    return len(accounts)
