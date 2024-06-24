from datetime import datetime, timedelta

import requests

from chalk import Cron, Now, online
from chalk.features import feature, features


@features
class User:
    id: int
    name: str
    email: str
    status: str
    last_login: datetime
    fico_score: int = feature(max_staleness="30d")


# Filter functions can take in any features as arguments, and must
# output True or False to indicate whether to consider a given entity
# in a scheduled run
def only_active_filter(
    last_login: User.last_login, status: User.status, now: Now
) -> bool:
    return status == "active" and last_login > (now - timedelta(days=30))


# You may want to run your cron jobs only on a subset of your userbase.
# Imagine, for example, that you wanted to regularly pull credit scores
# for only users who had logged in within the last 30 days.
#
# To do that, pass the keyword argument `cron` an instance of `Cron`,
# and provide a filter function. The filter function should take as arguments
# any feature values that it needs to output a boolean answer for whether
# an entity should be considered for scheduled runs.
#
# Note that in this example, our active filter depends on two features
# that are not part of our resolver's arguments.
@online(cron=Cron(schedule="29d 11h", filter=only_active_filter))
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
