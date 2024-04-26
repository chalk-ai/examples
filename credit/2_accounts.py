"""An example of connecting Users to Bank Accounts through Chalk.

In this example, we connect Users to Bank Accounts. On top of
this, we show how to use a connected postgres datasource to
resolve features.
"""

from datetime import datetime

from chalk import online
from chalk.features import features, DataFrame, has_many, FeatureTime
from chalk.sql import PostgreSQLSource

# This example assumes a postgres database has been added through the chalk
# dashboard where it was assigned a name of "CLOUD_DB". The database should
# contain an accounts table with 'id', 'bank_bank_account_number', 'decision',
# 'user_id', 'created_at', and 'updated_at' fields.

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


# this call connects the Accounts feature to the "account" table of the `PostgresSQLSource` instantiated above
pg.with_table(
    name="accounts",
    features=Account,
    column_to_feature={
        "id": Account.id,
        "bank_account_number": Account.bank_account_number,
        "user_id": Account.user_id,
        "created_at": Account.created_at,
        "updated_at": Account.updated_at,
    },
)


@features
class User:
    id: str
    name: str
    accounts: DataFrame[Account] = has_many(lambda: Account.user_id == User.id)

    # computed
    number_of_accounts: int


@online
def count_accounts(accounts: User.accounts) -> User.number_of_accounts:
    return len(accounts)

# ---------------------------------------------------------------------------------
# Let us assume that our postgres database also contains a `users` table with
# the fields: ['id', 'first_name', 'last_name', 'birthday', 'age']. We could
# update our base User feature class to include all the fields and use the same
# `with_table` syntax that we used to populate our `Account` feature. However,
# suppose we want to keep the User feature lean or that we want to apply some
# simple transformation on the raw data without using a python resolver.
#
# To accomplish this we can use what Chalk refers to as a `sql_file_resolver`
# (https://docs.chalk.ai/docs/sql#sql-file-resolvers). Essentially, we can
# resolve the User feature by placing a file called `get_user.chalk.sql` in our
# Chalk Directory and adding some metadata specifying the name of the resolved
# feature and the upstream raw data source. It would wind up looking like the
# following:
# ---------------------------------------------------------------------------------
#
# -- type: online
# -- resolvers: user
# -- source: CLOUD_DB
# select id, first_name||last_name as name FROM users;
