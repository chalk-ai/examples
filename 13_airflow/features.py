from chalk import online
from chalk.features import features


@features
class User:
    id: int
    name: str
    email: str
    email_domain: str


@online
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()
