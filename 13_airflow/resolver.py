from chalk import online
from chalk.features import features
from chalk.sql import PostgreSQLSource

pg = PostgreSQLSource()


@features
class User:
    id: int
    email: str
    email_domain: str


pg.with_table(
    name="users",
    features=User,
)


@online
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()
