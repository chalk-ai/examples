import requests

from chalk.features import features, feature

@features
class User:
    id: str
    socure_score: float = feature(max_staleness="30d")



@online
def get_socure_score(uid: User.id) -> Features[User.socure_score]:
    return (
        requests.get("https://api.socure.com", json={
            id: uid
        }).json()['socure_score']
    )