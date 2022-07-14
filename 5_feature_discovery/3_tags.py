from chalk.features import features, feature, tags


# Tags are assigned as code comments
@features
class RiskProfile1:
    id: int
    # :tags: group:risk
    email: str
    kyc_score: str


# Or explicitly set via `feature(tags=...)`
@features
class RiskProfile2:
    id: int
    email: str = feature(tags="group:risk")
    kyc_score: str


# A feature can have many tags
@features
class RiskProfile3:
    id: int
    # :tags: group:risk, pii
    email: str
    kyc_score: str


# Tags assigned on the class will apply to each of its features
@features(tags="group:risk")
class RiskProfile4:
    id: str
    kyc_score: float
    email_age_days: int


# Tags on the class add to tags on the feature
@features(tags="group:risk")
class RiskProfile5:
    id: str
    kyc_score: float
    email_age_days: int
    # :tags: pii
    email: str


# The function `chalk.features.tags(...)` returns the tags for a feature
assert tags(RiskProfile5) == ["group:risk"]
assert tags(RiskProfile5.id) == ["group:risk"]
assert tags(RiskProfile5.email) == ["pii", "group:risk"]
