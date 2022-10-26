from chalk import tags, is_primary, owner, description
from chalk.features import features


@features(owner="shuttle@nasa.gov", tags="group:rocketry")
class SpaceShuttle:
    id: str

    # The SHA1 of the software deployed to the shuttle.
    # Should align with a git commit on main.
    #
    # :owner: katherine.johnson@nasa.gov
    software_version: str

    # The volume of this shuttle in square meters.
    # :owner: architecture@nasa.gov
    # :tags: zillow-fact, size
    volume: str


# Pulling the description programmatically
assert len(description(SpaceShuttle.software_version)) > 0

# Pulling the tags for the feature class and features
assert tags(SpaceShuttle) == ["group:rocketry"]
assert tags(SpaceShuttle.volume) == ["zillow-fact", "size", "group:rocketry"]

# Pulling the owner for the feature class and features
assert owner(SpaceShuttle) == "shuttle@nasa.gov"
assert owner(SpaceShuttle.software_version) == "katherine.johnson@nasa.gov"

assert is_primary(SpaceShuttle.id)
