import requests

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features, feature


@features
class User:
    id: int
    name: str

    # Setting the maximum staleness to `infinity` means that you'll
    # always receive the latest value of the feature.
    fico_score: int = feature(max_staleness="infinity")


# Slow and expensive `User.fico_score` resolver from `1_basic_caching.py`
@realtime
def get_fico_score(name: User.name) -> User.fico_score:
    return requests.get("...").json()["fico"]


# This time, when the FICO score feature is requested,
# we'll receive the most recently computed value
# Infinite caching plays well with prefetching.
# See 7_prefetching.py for more detail
ChalkClient().query(
    input={User.name: "Katherine Johnson"},
    output=[User.fico_score],
)
