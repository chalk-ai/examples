import requests

from chalk import online
from chalk.features import features


@features
class User:
    id: str
    name: str
    email: str
    credit_score: str


# By default, resolvers with a `cron` parameter will sample the latest
# versions of the data. Imagine you had historically resolved the following
# features:
#
#   | Time | ID  | Email                | Name        |
#   | :--: | :-: | -------------------- | ----------- |
#   |  0   |  1  | elliot@chalk.ai      | Elliot      |
#   |  1   |  2  | andy@chalk.ai        | Andy        |
#   |  2   |  1  |                      | Elliot Marx |
#   |  3   |  2  | elliot.marx@chalk.ai |             |
#
# Then, we would sample the following pairs and invoke the resolver
# with these arguments:
#
#   | Email                | Name        |
#   | -------------------- | ----------- |
#   | elliot.marx@chalk.ai | Elliot Marx |
#   | andy@chalk.ai        | Andy        |
#
# Note that we don't sample (elliot.marx@chalk.ai, Elliot),
# for example, as those features are not the latest values
# for a given id.
#
# The argument to cron can use the Chalk duration type,
# or take a crontab-formatted string:
# i.e.: @online(cron="*/5 * * * *")


@online(cron="30d")
def get_credit_score(name: User.name, email: User.email) -> User.credit_score:
    return requests.get("https://experian.com").json()["score"]
