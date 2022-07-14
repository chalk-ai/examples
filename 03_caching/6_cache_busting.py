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
    return requests.get("https://experian.com").json()["score"]


# You can force cache invalidation by specifying a
# maximum staleness of 0 seconds at the time of making the query:
ChalkClient().query(
    input={User.id: 1, User.name: "Katherine Johnson"},
    output=[User.fico_score],
    # Cache busting is a special case of providing an override
    # max-staleness. See `4_override_max_staleness.py` for more information.
    staleness={User.fico_score: "0s"},
)
