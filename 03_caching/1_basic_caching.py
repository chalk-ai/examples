import requests

from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import feature, features


@features
class User:
    id: int
    name: str

    # Here, we can specify the default maximum staleness
    # that we'll tolerate for a feature.
    # You can also override this setting when you go to fetch
    # the feature! See 4_override_max_staleness.py for more info
    fico_score: int = feature(max_staleness="30d")


# This function is both slow and expensive to run,
# but because we're caching the `User.fico_score`
# feature, it won't run every time we need the feature!
@realtime
def get_fico_score(name: User.name) -> User.fico_score:
    response = requests.get(
        "https://experian.com/api/score",
        json={"name": name},
    ).json()
    return response["fico"]


if __name__ == "__main__":
    # The first time that we run this query,
    # `get_fico_score` will call out to Experian,
    # because the FICO score is not available.
    ChalkClient().query(
        input={User.name: "Katherine Johnson"},
        output=[User.fico_score],
    )

    # The second time that we run this query with
    # the same name, however, `get_fico_score` will
    # NOT call out to Experian, because we have computed
    # the FICO score for this user in the last 30 days.
    ChalkClient().query(
        input={User.name: "Katherine Johnson"},
        output=[User.fico_score],
    )
