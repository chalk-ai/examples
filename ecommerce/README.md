# E-commerce

Chalk can help you build realtime recommendation systems.

This guide shows you how to:
1). Implement user/seller features in chalk,
2). Add an Interaction feature and connect it to users,
3). Stream Interaction data from a Kafka queue.

In each section, you can find an `example_query.py` file. The file shows how the python chalk api could be used to
get information on the affinity between a user and a seller.

```python
from chalk import ChalkClient
from models import UserSeller

if __name__ == "__main__":
    client = ChalkClient()
    user_stores = client.query(
        input=[
            UserSeller(user_id="123", seller_id="456"),
            UserSeller(user_id="123", seller_id="457"),
            UserSeller(user_id="123", seller_id="458"),
            UserSeller(user_id="123", seller_id="458"),
            UserSeller(user_id="123", seller_id="456"),
            UserSeller(user_id="123", seller_id="461"),
            UserSeller(user_id="123", seller_id="460"),
        ],
        output=[UserSeller.user.id, UserSeller.seller.id, UserSeller.favorites_match]
    )
    print(user_stores)
```

## 1. Set up and query Users & Sellers

Create Chalk features for users and sellers and evaluate whether a user and seller have accordant categories.

- features: **[1_user_sellers/features.py](1_user_sellers/features.py)**
- resolvers: **[1_user_sellers/resolvers.py](1_user_sellers/resolvers.py)**
- datasources: **[1_user_sellers/datasources.py](1_user_sellers/datasources.py)**

### features.py

Create default User, Seller, and UserSeller features.

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

### resolvers.py

Create an online resolver for whether Users and Sellers have overlapping categories.

```python
from chalk import online
from models import UserSeller

@online
def get_similarity(
    fc: UserSeller.user.favorite_categories,
    fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match::wq
    return fc & fc2 # check whether sets overlap
```

### datasources.py

Create postgres datasource and resolve User and Seller from tables.

```python
from chalk.sql import PostgreSQLSource
from features import User, Seller

pg_database = PostgreSQLSource(name="CLOUD_DB")
pg_database.with_table(name="users", features=User)
pg_database.with_table(name="sellers", features=Seller)
```

## 2. Add User Seller Interactions

Add user seller interactions and update a UserSeller ranking based on the number of interactions
that have occurred between a user and a seller.

- [features](2_interactions/features.py)
- [resolvers](2_interactions/resolvers.py)
- [datasources](2_interactions/datasources.py)

### features.py

Add interactions feature and connect interactions to user

```python
from chalk.features import features, DataFrame, FeatureTime

@features
class User:
    id: str
    age: int
    favorite_categories: set[str]
    interactions: DataFrame["Interaction"]

class InteractionKind(Enum):
    LIKE = "LIKE"
    VIEW = "VIEW"
    PURCHASE = "PURCHASE"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
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

### resolvers.py

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

### datasources.py

Connect postgres to interactions table

```python
pg_database.with_table(name="user_interactions", features=Interaction)
```

## 3. Stream User Seller Interaction Data

Enrich User Interaction data with stream data.

- [datasources](3_streams/datasources.py)
- [models](3_streams/models.py)
- [resolvers](3_streams/resolvers.py)
- [features](3_streams/features.py)

### datasources.py

Add a Kafka stream data source to stream interactions

```python
from chalk.streams import KafkaSource
interaction_stream = KafkaSource(name="interactions")
```

### models.py

Create a pydantic Model to validate and process stream messages

```python
from pydantic import BaseModel

class InteractionMessage(BaseModel):
    id: str
    user_id: str
    seller_id: str
    interaction_kind: str
```

### resolvers.py

Add a stream resolver to process interactions

```python
from chalk.features import Features
from chalk import stream, online
from features import UserSeller, Interaction, InteractionKind
from datasources import interaction_stream
from models import InteractionMessage
import uuid


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
