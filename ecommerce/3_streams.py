from enum import Enum
from datetime import datetime

from chalk import online
from chalk.features.resolver import make_stream_resolver
from chalk.features import DataFrame, FeatureTime, features, _
from chalk.streams import KafkaSource
from pydantic import BaseModel


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
    user_id: User.id
    user: User
    seller_id: Seller.id
    seller: Seller
    favorites_match: bool
    user_seller_score: int

    interactions: "DataFrame[Interaction]" = has_many(
        lambda: (User.id == Interaction.user_id) & (Seller.id == Interaction.seller_id)
    )

    number_of_interactions: int = _.interactions.count()


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
    user_id: User.id
    user: User
    seller_id: Seller.id
    seller: Seller
    interaction_kind: InteractionKind
    on: FeatureTime


interaction_stream = KafkaSource(name="interactions")


class InteractionMessage(BaseModel):
    id: str
    user_id: str
    seller_id: str
    interaction_kind: str
    ingestion_time: datetime


process_interactions = make_stream_resolver(
    name="process_interactions",
    source=interaction_stream,
    message_type=InteractionMessage,
    output_features={
        Interaction.id: _.message.id,
        Interaction.user_id: _.message.user_id,
        Interaction.seller_id: _.message.seller_id,
        Interaction.interaction_kind: _.message.interaction_kind,
        Interaction.on: _.ingestion_time,
    },
)


@online
def get_similarity(
    fc: UserSeller.user.favorite_categories, fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match:
    return len(fc & fc2) > 0


if __name__ == "__main__":
    from chalk.client import ChalkClient

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
        output=[
            UserSeller.user.id,
            UserSeller.seller.id,
            UserSeller.favorites_match,
            UserSeller.number_of_interactions,
        ],
    )
    print(user_stores)
