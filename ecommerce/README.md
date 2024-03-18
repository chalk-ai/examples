# E-commerce

Chalk can help you build realtime recommendation systems

## 1. Set up and query Users & Sellers

Create Chalk features for users and sellers and evaluate whether a user and seller have accordant categories.

- features: **[1_user_sellers/features.py](1_user_sellers/features.py)**
- resolvers: **[1_user_sellers/resolvers.py](1_user_sellers/resolvers.py)**
- datasources: **[1_user_sellers/datasources.py](1_user_sellers/datasources.py)**

### features.py

```python
@realtime
def get_plaid_income(
        txns: User.transactions[
            PlaidTransaction.is_payroll is True,
            after(days_ago=30),
        ],
) -> User.computed_income_30:
    return txns[PlaidTransaction.amount].sum()
```

### resolvers.py

### datasources.py

## 2. Add User Seller Interactions

Add user-seller interactions and update user-seller ranking.

- [features](2_interactions/features.py)
- [resolvers](2_interactions/resolvers.py)
- [datasources](2_interactions/datasources.py)

### features.py

Add interactions feature and connect interactions to user

```python
from chalk.features import features, DataFrame,  FeatureTime

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
