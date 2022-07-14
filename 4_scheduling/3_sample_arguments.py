import requests
from datetime import datetime

from chalk import realtime, Cron
from chalk.features import features, feature, DataFrame
from chalk.sql import PostgreSQLSource


@features
class User:
    id: int
    name: str
    email: str
    last_login: datetime
    fico_score: int = feature(max_staleness="30d")


session = PostgreSQLSource()


def get_active_users() -> DataFrame[User.id]:
    return session.query_string(
        "select users.id from users where users.active = true",
        fields={"id": User.id},
    ).all()


# The sample function can pull the primary keys or any subset of
# the arguments that you'd like to sample, and Chalk will sample
# the other arguments.
@realtime(cron=Cron(schedule="29d 11h", sample=get_active_users))
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
