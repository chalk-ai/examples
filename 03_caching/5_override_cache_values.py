from enum import Enum

import requests

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import feature, features


class FICOBucket(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@features
class User:
    id: int
    name: str
    fico_score: int = feature(max_staleness="30d")
    fico_bucket: FICOBucket


@realtime
def get_fico_score(name: User.name) -> User.fico_score:
    return requests.get(...).json()["score"]


@realtime
def discretize_fico_score(score: User.fico_score) -> User.fico_bucket:
    if score > 700:
        return FICOBucket.HIGH
    if score > 600:
        return FICOBucket.MEDIUM
    return FICOBucket.LOW


if __name__ == "__main__":
    # You can also override the cached _value_ (in addition to the cache
    # duration, as described in 4_override_max_staleness) by providing
    # the value as an input to the query.
    #
    # Here, we specify that the FICO score is 700. That value is passed
    # to the resolver `discritize_fico_score` to compute `User.fico_bucket`,
    # instead of running `get_fico_score`.
    ChalkClient().query(
        input={User.name: "Katherine Johnson", User.fico_score: 700},
        output=[User.fico_bucket],
    )
