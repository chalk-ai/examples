from enum import Enum

import requests

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features, feature


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


# Specifying the max-staleness value also holds when
# the cached feature is an intermediate result for your
# query, but not a desired output.
ChalkClient().query(
    input={User.name: "Katherine Johnson"},
    # User.fico_score is not requested in the output
    output=[User.risk_score],
    # ...but is necessary to compute User.risk_score.
    # The requested feature `User.risk_score` is computed
    # by running `discretize_fico_score`, which in turn
    # depends on `User.fico_score`.
    staleness={User.fico_score: "10m"},
)
