import requests
from datetime import datetime

from chalk import realtime
from chalk.features import features, feature


@features
class User:
    id: int
    name: str
    email: str
    last_login: datetime
    fico_score: int = feature(max_staleness="30d")


# You can warm the cache by scheduling a resolver to run
# more frequently than the max-staleness.
# Here, the maximum-staleness for the FICO score is 30 days,
# and the cron schedule means that this function will run
# every 29 days and 11 hours. So, the cache will always be warm.
@realtime(cron="29d 11h")
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
