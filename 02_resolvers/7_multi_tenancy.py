from datetime import datetime

from chalk import online
from chalk.client import ChalkClient, OnlineQueryContext
from chalk.features import features, DataFrame, Features, has_many
from chalk.sql import MySQLSource, PostgreSQLSource


@features
class WatchSession:
    id: int
    ended_at: datetime
    started_at: datetime
    user_id: int
    duration_seconds: float


@features
class User:
    id: int
    count_long_sessions: int
    sessions: DataFrame[WatchSession] = has_many(lambda: WatchSession.user_id == User.id)


# Imagine that we have two video streaming customers, HBO and Disney.
# Disney has given us credentials to their PostgreSQL database, and
# HBO to their MySQL database. We can reference these integrations
# via named sources, and add the secrets through the Chalk dashboard.
# Those secrets will only be available in the environments in which
# they are configured, so there is no chance of accidentally using
# the Disney PostgreSQL database in the HBO environment.
disney_pg = PostgreSQLSource(name="disney")
hbo_mysql = MySQLSource(name="hbo")


# Now, we can write resolvers specific to our customers: one for Disney
# and one for HBO.
@online(environment="disney")
def get_disney_sessions_for_user(
    u: User.id,
) -> DataFrame[WatchSession.id, WatchSession.ended_at, WatchSession.started_at]:
    return disney_pg.query_string(
        "SELECT * FROM sessions where user_id = :user_id",
        args={"user_id": u},
        fields={
            "id": WatchSession.id,
            "completed_at": WatchSession.ended_at,
            "began_at": WatchSession.started_at,
        },
    ).all()


@online(environment="hbo")
def get_hbo_sessions_for_user(
    u: User.id,
) -> Features[WatchSession.id, WatchSession.ended_at, WatchSession.started_at]:
    return hbo_mysql.query_string(
        "SELECT * FROM show_views where uid = :user_id",
        args={"user_id": u},
        fields={
            "id": WatchSession.id,
            "ended": WatchSession.ended_at,
            "started": WatchSession.started_at,
        },
    ).all()


# These function is shared between all environments.
# Each of these resolvers is deployed into each of
# the environments, but no data is shared between
# the environments. This pattern allows for consolidation
# of your complicated business logic on top of a
# unified schema while maintaining strict isolation
# of data.
@online
def get_duration_watched(
    started: WatchSession.started_at, ended: WatchSession.ended_at
) -> WatchSession.duration_seconds:
    return (ended - started).total_seconds()


@online
def num_long_sessions(
    long_sessions: User.sessions[WatchSession.duration_seconds > 3600],
) -> User.count_long_sessions:
    return long_sessions.count()


# When you go to make a query, you can specify the
# environment in which to evaluate the query, which will
# determine which cluster to send your query to.
ChalkClient().query(
    input={User.id: 123},
    output=[User.count_long_sessions],
    context=OnlineQueryContext(environment="hbo"),
)

# You can also scope your access tokens to an environment,
# and don't need to specify an environment id when the
# token is valid in only one environment.
#
# For example, here the client_id and client_secret could
# be scoped to the "disney" environment.
ChalkClient(client_id="...", client_secret="...").query(
    input={User.id: 345},
    output=[User.count_long_sessions],
)
