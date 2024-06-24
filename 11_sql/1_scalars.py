from chalk import online
from chalk.features import features
from chalk.sql import SQLiteInMemorySource


@features
class User:
    id: str
    viewed_minutes: float


db = SQLiteInMemorySource()


@realtime
def get_views(user: User.id) -> User.viewed_minutes:
    return db.query_string(
        "select sum(mins) as viewed_minutes from view_counts where uid = :uid",
        args=dict(uid=user),
        # Chalk lines up the name of your returned SQL columns
        # with the features that your resolver says it returns
        # It they don't line up, you can explicitly map any
        # of the columns with the line below:
        #    fields=dict(viewed_minutes=User.viewed_minutes),
    ).one()


@online
def get_views(user: User.id) -> User.viewed_minutes:
    """
    This resolver executes the same query as above,
    but moves the SQL string into the file `user_views.sql`.
    """
    return db.query_sql_file(
        "user_views.sql",
        args=dict(uid=user),
        fields=dict(viewed_minutes=User.viewed_minutes),
    ).one()
