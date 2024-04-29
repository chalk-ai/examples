"""An example of connecting Users to Credit Reports from a
third part API (in this case socure).

In this example, we use the requests library to make
get a client's socure score from the socure REST API. This
example shows how you can run arbitrary python code (and connect
to third party APIs) in a python resolver.
"""

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
    """This resolver approximates how one might make a REST
    API call to socure in a python resolver for a specific
    user.
    """
    return requests.get(
        "https://api.socure.com",
        json={
            "id": uid,
        },
    ).json()["socure_score"]
