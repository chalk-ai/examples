from chalk import realtime
from chalk.features import Features, features


# First, we'll define a set of features and resolvers:
@features
class HomeFeatures:
    id: str
    address: str
    price: int
    sq_ft: int


@realtime
def get_address(hid: HomeFeatures.id) -> HomeFeatures.address:
    return "Bridge Street" if hid == 1 else "Filbert Street"


@realtime
def get_home_data(
    hid: HomeFeatures.id,
) -> Features[HomeFeatures.price, HomeFeatures.sq_ft]:
    return HomeFeatures(price=200_000, sq_ft=2_000)


# Chalk lets you specify your feature pipelines using
# idiomatic Python. This means that you can unit test
# individual resolvers and combinations of resolvers,
# since they’re just Python functions.
def test_single_output():
    assert get_address(2) == "Filbert Street"


# Dataclasses support equality, which can be used
# to test resolvers which return multiple features.
def test_multiple_output():
    result = get_home_data(2)
    assert result.price == 200_000
    assert result.sq_ft == 2_000
    assert result != HomeFeatures(
        address="hello",
        price=200_000,
        sq_ft=2_000,
    )
    assert result == HomeFeatures(
        price=200_000,
        sq_ft=2_000,
    )
