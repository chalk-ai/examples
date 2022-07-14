from random import random

from chalk import realtime
from chalk.client import ChalkClient, OnlineQueryContext
from chalk.features import features
from mocks import lexus_nexus


@features
class User:
    id: int
    email: str
    email_domain: str
    email_risk_score: float
    banned_email: bool


# If a request for features is made under the tag
# `mock`, then this resolver will run.
@realtime(tags="mock")
def mock_check_banned_email(domain: User.email_domain) -> User.banned_email:
    if domain == "chalk.ai":
        return False
    if domain == "fraudster.com":
        return True
    return random() < 0.1


@realtime
def get_email_risk_score(email: User.email) -> User.email_risk_score:
    return lexus_nexus.get_email_risk(email).risk_score


# If a request for features is made with _without_ the tag
# than `mock`, then this resolver will run.
#
# Note that the two resolvers that resolve the feature
# User.banned_email require different features as input!
@realtime
def check_banned_email(score: User.email_risk_score) -> User.banned_email:
    return score >= 0.8


result = ChalkClient().query(
    input={User.email: "katherine.johnson@nasa.gov"},
    output=[User.banned_email],
)
assert result.get_feature_value(User.banned_email) == False

result = ChalkClient().query(
    input={User.email: "attacker@fraudster.com"},
    output=[User.banned_email],
    context=OnlineQueryContext(tags=["mock"]),
)
assert result.get_feature_value(User.banned_email) == True
