# 3. Stream User Seller Interaction Data

Enrich User Interaction data with stream data.

- [datasources](3_streams/datasources.py)
- [models](3_streams/models.py)
- [resolvers](3_streams/resolvers.py)
- [features](3_streams/features.py)

## datasources.py

Add a Kafka stream data source to stream interactions

```python
from chalk.streams import KafkaSource
interaction_stream = KafkaSource(name="interactions")
```

## models.py

Create a pydantic Model to validate and process stream messages

```python
from pydantic import BaseModel

class InteractionMessage(BaseModel):
    id: str
    user_id: str
    seller_id: str
    interaction_kind: str
```

## resolvers.py

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
