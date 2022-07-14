from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features


@features
class User:
    id: int
    email: str
    email_domain: str


# This resolver computes one features, `User.email_domain`.
# To compute that feature, it takes a data dependency on `User.email`.
@realtime
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()


# Once you've deployed your features, you can query them by providing
# the data you know that's already in scope, and asking for any feature
# value that can be computed downstream from that data
result = ChalkClient().query(
    # Here, we say that we know the email is `jessie@chalk.ai`.
    # In practice, typically this is just the id of the entity
    # that you care about
    input={User.email: "jessie@chalk.ai"},
    # Here we ask Chalk to compute the `User.email_domain` from this
    # downstream feature
    output=[User.email_domain],
)

# From the resulting object, we can pull the `User.email_domain`
# feature, and see that it is in fact `chalk.ai`.
assert result.get_feature_value(User.email_domain) == "chalk.ai"
