from chalk import online
from chalk.features import DataFrame, features
from chalk.sql import SQLiteInMemorySource


@features
class User:
    id: str
    viewed_minutes: float


db = SQLiteInMemorySource()


@online
def get_views() -> DataFrame[User]:
    """
    Chalk is able to perform push down filters on the returned type here,
    so even though we're returning the viewed minutes for every user,
    Chalk will only read the rows that it needs to serve queries.
    """
    return db.query_string(
        """
        select id, sum(mins) as viewed_minutes
        from view_counts
        group by id
        """,
    ).all()
