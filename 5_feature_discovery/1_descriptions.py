from chalk.features import features, feature, description


@features
class RocketShip1:
    id: int
    # Comments above a feature are applied assigned
    # to the features above which they sit.
    software_version: str


@features
class RocketShip2:
    software_version: str = feature(
        description="""
        You can use explicit comments too! Explicit comments
        take precedence over comments parsed from comments in
        the code (as above)
        """
    )


# The function `chalk.features.description(...)` returns the description text
print(description(RocketShip1.software_version))
