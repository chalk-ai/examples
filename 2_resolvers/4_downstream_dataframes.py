from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features


@features
class User:
    id: int
    email: str
    email_domain: str
    banned_email: bool


@realtime
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()


@realtime
def is_banned_email(domain: User.email_domain) -> User.banned_email:
    return domain in {
        "pergi.id",
        "convoitucpa.com",
        "vshgl.com",
        "nieise.com",
        "bookue.site",
        "umaasa.com",
    }


result = ChalkClient().query(
    input={User.email: "katherine.johnson@nasa.gov"},
    output=[User.banned_email],
)
assert result.get_feature_value(User.banned_email) == False

result = ChalkClient().query(
    input={User.email: "attacker@vshgl.com"},
    output=[User.banned_email],
)
assert result.get_feature_value(User.banned_email) == True
