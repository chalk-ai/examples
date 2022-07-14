from chalk import realtime
from chalk.client import ChalkClient
from chalk.features import features, Features
from mocks import user_service


@features
class User:
    id: int
    name: str
    email: str


# Unlike with our scalar resolvers, here we need to wrap our output in
# the class `Features[...]`.
@realtime
def get_user_details(uid: User.id) -> Features[User.name, User.email]:
    details = user_service.get_identity(uid)
    # Note that we don't need to supply all arguments to `User`.
    # The field `id` on `User` is non-optional, and doesn't have a
    # default value, but these classes accept partial application.
    # See `01_features/8_constructing_features.py` for more info.
    return User(
        name=details.name,
        email_domain=details.email,
    )


# We can then query features as we did in the previous example.
result = ChalkClient().query(
    input={User.id: 4},
    output=[User.name, User.email],
)
