from enum import Enum

from chalk import online
from chalk.features import DataFrame, FeatureTime, features, _


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
    user: user
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
            UserSeller(user_id="1", seller_id="456"),
            UserSeller(user_id="2", seller_id="457"),
            UserSeller(user_id="3", seller_id="460"),
        ],
        output=[
            UserSeller.user.id,
            UserSeller.seller.id,
            UserSeller.favorites_match,
            UserSeller.number_of_interactions,
        ],
    )
    print(user_stores)
