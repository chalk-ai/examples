import requests

from chalk import realtime
from chalk.features import features


@features
class User:
    id: str
    name: str
    email: str
    credit_score: str


# By default, resolvers with a `cron` parameter will be sampled with all
# unique historical sets of examples that could have occurred at a time.
# In this example, imagine that we observed the following names and emails
# at the times 0, 1, 2:
#
#   | Time | Email                | Name        |
#   | :--: | -------------------- | ----------- |
#   |  0   | elliot@chalk.ai      | Elliot      |
#   |  1   |                      | Elliot Marx |
#   |  2   | elliot.marx@chalk.ai |             |
#
# Then, we would sample the following pairs and invoke the resolver
# with these arguments:
#
#   | Email                | Name        |
#   | -------------------- | ----------- |
#   | elliot@chalk.ai      | Elliot      |
#   | elliot@chalk.ai      | Elliot Marx |
#   | elliot.marx@chalk.ai | Elliot Marx |
#
# Note that we don't sample (elliot.marx@chalk.ai, Elliot),
# As there was no time at which that data could have existed
# at the same time. Finally, we can change the arguments to
# this resolver over time, and Chalk will sample the
@realtime(cron="30d")
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]


# The argument to cron can use the Chalk duration type,
# or take a crontab-formatted string:
@realtime(cron="*/5 * * * *")
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
