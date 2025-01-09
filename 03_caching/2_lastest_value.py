import requests

from chalk import online
from chalk.client import ChalkClient
from chalk.features import feature, features


@features
class User:
    id: int
    name: str

    # Setting the maximum staleness to `infinity` means that this
    # value is calculated once and then read from the online store
    # for subsequent requests.
    fico_score: int = feature(max_staleness="infinity")


# Slow and expensive `User.fico_score` resolver from `1_basic_caching.py`
@online
def get_fico_score(name: User.name) -> User.fico_score:
    return requests.get("...").json()["fico"]


if __name__ == "__main__":
    ChalkClient().query(
        input={User.name: "Katherine Johnson"},
        output=[User.fico_score],
    )
