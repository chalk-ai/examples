"""An example of connecting Users to Bank Accounts through Chalk

In this example, we are connecting Users to Bank Accounts. On
top of this, we are connecting to a postgres datasource,
specified by the user
on their plaid transactions.
"""

from datetime import datetime

from chalk import online
from chalk.features import features, DataFrame, has_many, FeatureTime
from chalk.sql import PostgreSQLSource

# Bank accounts are stored in SQL, Credentials are stored as Chalk secrets. Adding
# a datasource, can be done through the datasource tab of the Chalk Dashboard.
#
# This example, assumes a postgres database has been added through the chalk
# dashboard, where it has given a name of "CLOUD_DB". The database should
# contain a accounts table with 'id', 'bank_bank_account_number', 'decision', 'user_id',
# 'created_at', and 'updated_at' fields.

pg = PostgreSQLSource(name="CLOUD_DB")


@features
class Account:
    id: int
    bank_account_number: int
    decision: str
    user_id: str
    created_at: datetime
    # https://docs.chalk.ai/docs/features#feature-time
    updated_at: FeatureTime


pg.with_table(name="accounts", features=Account)


@features
class User:
    id: str
    name: str
    accounts: DataFrame[Account] = has_many(lambda: Account.user_id == User.id)

    # computed
    number_of_accounts: int


# ---------------------------------------------------------------------------------
# Let us assume that our postgres database also contains a `User` table. For
# example, a table called `user` with the fields: ['id', 'first_name', 'last_name',
# 'birthday', 'age']. We could update our base class to include all the fields and
# use the same `with_table` syntax we used to populate our Account feature.
# However, suppose we want to keep the User feature lean or that we want to apply
# some simple transformation on the raw data without using a python resolver.
#
# To accomplish this we can use what Chalk refers to as a `sql_file_resolver`
# (https://docs.chalk.ai/docs/sql#sql-file-resolvers). Essentially, we would
# add a file called `get_user.chalk.sql` in our Chalk Directory and add
# some metadata specifying the name of the resolved feature and the
# upstream raw data source. It would wind up looking like the following:
# ---------------------------------------------------------------------------------
#
# -- type: online
# -- resolvers: user
# -- source: CLOUD_DB
# select id, first_name||last_name as name FROM users;

@online
def count_accounts(accounts: User.accounts) -> User.number_of_accounts:
    return len(accounts)
