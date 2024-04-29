import requests

from chalk import online
from chalk.features import features, feature


@features
class User:
    id: str

    # the max staleness assignment on the feature means
    # that a new socure score is only computed if one
    # hasn't been computed in the last 30 days.
    socure_score: float = feature(max_staleness="30d")


@online
def get_socure_score(uid: User.id) -> User.socure_score:
    """

    """
    return requests.get(
        "https://api.socure.com",
        json={
            "id": uid,
        },
    ).json()["socure_score"]
