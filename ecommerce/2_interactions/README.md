# Adding User/Seller Interactions

Add user seller interactions and create a UserSeller feature (number_of_interactions) which returns the number of interactions
that have occurred between a user and a seller: this could be used for ranking.

- [features](2_interactions/features.py)
- [resolvers](2_interactions/resolvers.py)
- [datasources](2_interactions/datasources.py)

## features.py

Add interactions feature and connect interactions to user

```python
from chalk.features import features, DataFrame, FeatureTime

@features
class User:
    id: str
    age: int
    favorite_categories: set[str]
    interactions: DataFrame["Interaction"]

class User:
    id: str
    age: int
    favorite_categories: set[str]
    interactions: DataFrame["Interaction"]

@features
class UserSeller:
    id: str
    user_id: str
    user: User.id
    seller_id: str
    seller: Seller.id
    favorites_match: bool
    number_of_interactions: int

class InteractionKind(Enum):
    LIKE = "LIKE"
    VIEW = "VIEW"
    PURCHASE = "PURCHASE"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, _):
        return cls.OTHER

@features
class Interaction:
    id: str
    user: User.id
    user_id: str
    seller: Seller.id
    seller_id: Seller.id
    interaction_kind: InteractionKind
    on: FeatureTime
```

## resolvers.py

Add interactions resolver

```python
from features import UserSeller, Interaction

@online
def get_number_of_interactions(
    user_interactions: UserSeller.user.interactions,
    seller_id: UserSeller.seller.id,
) -> UserSeller.number_of_interactions:
    return len(user_interactions.loc[Interaction.seller_id == seller_id])
```

## datasources.py

Resolve Interaction with the "user_interactions" table in the postgres datasource.

```python
pg_database.with_table(name="user_interactions", features=Interaction)
```
