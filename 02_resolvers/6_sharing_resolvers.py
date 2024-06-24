from chalk import online
from chalk.client import ChalkClient
from chalk.features import DataFrame, FeatureTime, after, features, has_many, has_one
from chalk.sql import PostgreSQLSource


# Imagine that we have two models:
#   1. send_reminder_email: decides when we should send our next reminder email
#   2. expected_loan_repayment: predicts the amount of money we expect to collect
#
# First, we'll lay out some feature classes for this problem:
@features
class EmailRecord:
    id: str
    user_id: str
    user: "User"
    sent_at: FeatureTime


@features
class User:
    id: str
    name: str
    emails_sent_last_10_days: int
    email_history: DataFrame[EmailRecord] = has_many(
        lambda: EmailRecord.user_id == User.id
    )


# The business logic for a feature is written only once,
# though it can be referenced many times.
@online
def get_emails_sent_last_10_days(
    emails: User.email_history[after(days_ago=10)],
) -> User.emails_sent_last_10_days:
    return emails.count()


# For our second model on expected loan repayment, we'll first model
# another feature class around loans:
@features
class Loan:
    id: int
    user_id: str
    amount: float
    user: User = has_one(lambda: User.id == Loan.user_id)


# Here, we leverage the work we did to build the
# feature `User.emails_sent_last_10_days` from the
# first model by requesting
# `Loan.user.emails_sent_last_10_days`.
# We configure this postgres source in the Chalk dashboard.
db = PostgreSQLSource()


# Work for sql queries is shared in the same way.
# For example, we need to be able to resolve the
# fields of `EmailRecord`.
@online
def get_email_record(user: User.id) -> DataFrame[EmailRecord]:
    return db.query_string(
        "select id, sent_at, user_id from email_record where user=:uid",
        fields=dict(
            id=EmailRecord.id,
            sent_at=EmailRecord.sent_at,
            user_id=EmailRecord.user_id,
        ),
        args=dict(uid=user),
    ).all()


if __name__ == "__main__":

    # For this first model, we request the `User.name`
    # and `User.emails_sent_last_10_days` features under
    # the query name `send_reminder_email`.
    ChalkClient().query(
        input={User.id: 1},
        output=[
            User.emails_sent_last_10_days,
            User.name,
        ],
        # This optional `query_name` associates the data
        # that we requested with a given model for monitoring
        # and migrations.
        query_name="send_reminder_email",
    )

    ChalkClient().query(
        input={Loan.id: "1"},
        output=[
            Loan.user.emails_sent_last_10_days,
            Loan.amount,
        ],
        query_name="expected_loan_repayment",
    )

    # Here, we're running a really basic query that just maps columns to features.
    # For these simple queries, there's a shortcut to automatically ingest these
    # tables:
    db.with_table(name="email_record", features=EmailRecord)
