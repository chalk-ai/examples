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
