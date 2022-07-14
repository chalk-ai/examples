from datetime import date

from chalk.features import features, feature, owner


@features
class User:
    id: str
    # Owners are specified via code comments:
    # :owner: katherine.johnson@nasa.gov
    name: str


@features
class User1:
    id: str
    # or explicitly with `feature(owner=...)`:
    name: str = feature(owner="katherine.johnson@nasa.gov")


# Setting an owner through the `@features` decorator
# determines the owner all the features on the class
@features(owner="katherine.johnson@nasa.gov")
class User2:
    id: str  # assigned the owner katherine.johnson@nasa.gov
    name: str  # assigned the owner katherine.johnson@nasa.gov


# Owners on features are more specific than owners
# set via the `@features` decorator.
@features(owner="katherine.johnson@nasa.gov")
class User3:
    # Katherine is the owner of the id and dob feature,
    # because she is the owner set in the `@features` decorator
    id: str
    dob: date

    # Annie is the owner of this feature because she is set
    # as the owner at the feature level, which is more specific
    # than the owner from the feature class
    # :owner: annie.easley@nasa.gov
    name: str


# The function `chalk.features.owner(...)` returns the owner of a feature
assert owner(User3.name) == "annie.easley@nasa.gov"
assert owner(User3.id) == "katherine.johnson@nasa.gov"
