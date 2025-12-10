from chalk import online
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
    user_id: User.id
    user: User
    seller_id: Seller.id
    seller: Seller
    favorites_match: bool


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
            UserSeller(user_id="1", seller_id="457"),
            UserSeller(user_id="1", seller_id="458"),
        ],
        output=[UserSeller.user.id, UserSeller.seller.id, UserSeller.favorites_match],
    )
    print(user_stores)
