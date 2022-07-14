import requests

from chalk import realtime
from chalk.features import features, feature


@features
class User:
    id: str
    socure_score: float = feature(max_staleness="30d")


# We'll only run this resolver if there hasn't been a Socure
# score computed in the last 30 days
@realtime
def get_socure_score(uid: User.id) -> User.socure_score:
    return requests.get(
        "https://api.socure.com",
        json={
            "id": uid,
        },
    ).json()["socure_score"]
