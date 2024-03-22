from chalk import stream, online, ChalkClient
from chalk.sql import PostgreSQLSource
from chalk.streams import KafkaSource
from chalk.features import Features, features, DataFrame, FeatureTime, Features
from enum import Enum
import uuid
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
    interactions: DataFrame["Interaction"]


@features
class UserSeller:
    id: str
    user_id: str
    user: User.id
    seller_id: str
    seller: Seller.id
    favorites_match: bool
    user_seller_score: int


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


pg_database = PostgreSQLSource(name="CLOUD_DB")
pg_database.with_table(name="users", features=User)
pg_database.with_table(name="sellers", features=Seller)
pg_database.with_table(name="user_interactions", features=Interaction)
interaction_stream = KafkaSource(name="interactions")


class InteractionMessage(BaseModel):
    id: str
    user_id: str
    seller_id: str
    interaction_kind: str


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


@online
def get_number_of_interactions(
    user_interactions: UserSeller.user.interactions,
    seller_id: UserSeller.seller.id,
) -> UserSeller.number_of_interactions:
    return len(user_interactions.loc[Interaction.seller_id == seller_id])


@online
def get_similarity(
    fc: UserSeller.user.favorite_categories, fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match:
    return fc & fc2  # check whether sets overlap


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
        output=[
            UserSeller.user.id,
            UserSeller.seller.id,
            UserSeller.favorites_match,
            UserSeller.number_of_interactions,
        ],
    )
    print(user_stores)
