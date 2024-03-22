# E-commerce

Chalk can help you build realtime recommendation systems.

This guide shows you how to:
1). Implement User and Seller features in Chalk,
2). Add an Interaction feature and connect it to users,
3). Stream Interaction data from a Kafka queue.

In each section, you can find an `example_query.py` file. The file shows how the Chalk python client API can be used to
get information on the affinity between a User and a Seller.

## 1. Set up and query Users & Sellers

Create Chalk features for Users and Sellers and evaluate whether a user and seller have accordant categories.

**[1_user_sellers.py](1_user_sellers.py)**

```python
from chalk.features import features


@features
class Seller:
    id: str
    categories: set[str]


@features
class User:
    id: str
    age: int
    favorite_categories: set[str]

@features
class UserSeller:
    id: str
    user_id: str
    user: User.id
    seller_id: str
    seller: Seller.id
    favorites_match: bool
```

## 2. Add User Seller Interactions

Add user seller interactions and use a resolver to identify the number of interactions
that have occurred between a user and a seller.

**[2_interactions.py](2_interactions.py)**

```python
from chalk.features import features, DataFrame, FeatureTime

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

@online
def get_number_of_interactions(
    user_interactions: UserSeller.user.interactions,
    seller_id: UserSeller.seller.id,
) -> UserSeller.number_of_interactions:
    return len(user_interactions.loc[Interaction.seller_id == seller_id])
```

## 3. Stream User Seller Interaction Data

Enrich User Interaction data with stream data.

**[3_streams.py](3_streams.py)**

```python
from chalk.streams import KafkaSource
from chalk.features import Features
from chalk import stream, online
import uuid

interaction_stream = KafkaSource(name="interactions")

@stream(source=interaction_stream)
def interactions_handler(
    message: InteractionMessage,
) -> Features[Interaction]:
    return Interaction(
        id=uuid.uuid4(),
        interaction_kind=message.interaction_kind,
        user_id=message.user_id,
        seller_id=message.seller_id,
    )
```
