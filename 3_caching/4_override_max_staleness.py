import requests

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features, feature


@features
class User:
    id: int
    name: str
    fico_score: int = feature(max_staleness="30d")


@realtime
def get_fico_score(name: User.name) -> User.fico_score:
    return requests.get(...).json()["score"]


# By default, the staleness will be taken to be the value given
# on the feature class. In this case, user.fico_score is cached
# for 30 days. But if you have a model that needs fresher data,
# you can specify the desired staleness at the time of making
# the query. For example, here we request a staleness of only
# 10 minutes.
ChalkClient().query(
    input={User.name: "Katherine Johnson"},
    output=[User.fico_score],
    staleness={User.fico_score: "10m"},
)

# If you didn't specify the staleness, the default staleness
# of 30 days would apply
ChalkClient().query(
    input={User.name: "Katherine Johnson"},
    output=[User.fico_score],
)
