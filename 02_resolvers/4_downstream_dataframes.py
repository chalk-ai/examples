from chalk import online
from chalk.client import ChalkClient
from chalk.features import DataFrame, features, has_many


@features
class Email:
    id: str
    uid: str
    domain: str
    is_banned: bool
    value: str


@features
class User:
    id: str
    banned: bool
    emails: DataFrame[Email] = has_many(lambda: Email.uid == User.id)


@online
def is_banned_email(domain: Email.domain) -> Email.is_banned:
    return domain in {
        "pergi.id",
        "convoitucpa.com",
        "vshgl.com",
        "nieise.com",
        "bookue.site",
        "umaasa.com",
    }


# Here, we say a user is banned if the user has any emails that are banned.
# Note that all of this can be computed real-time, and Chalk will run the
# `is_banned_email` resolver for each of the emails that the user has.
@online
def banned_user(domains: User.emails[Email.is_banned == True]) -> User.banned:
    return len(domains) > 0


if __name__ == "__main__":
    result = ChalkClient().query(
        input={User.id: "1"},
        output=[User.banned],
    )
