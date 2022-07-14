from chalk import realtime
from chalk.features import features
from chalk.sql import SQLiteInMemorySource


@features
class User:
    id: str
    viewed_minutes: float


session = SQLiteInMemorySource()


@realtime
def get_views(user: User.id) -> User.viewed_minutes:
    return session.query_string(
        "select sum(mins) as viewed_minutes from view_counts where uid = :uid",
        args=dict(uid=user),
        fields=dict(viewed_minutes=User.viewed_minutes),
    ).one()


@realtime
def get_views(user: User.id) -> User.viewed_minutes:
    return session.query_sql_file(
        "user_views.sql",
        args=dict(uid=user),
        fields=dict(viewed_minutes=User.viewed_minutes),
    ).one()
