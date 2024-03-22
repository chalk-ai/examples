from chalk import ChalkClient, online
from chalk.sql import PostgreSQLSource
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


@online
def get_similarity(
    fc: UserSeller.user.favorite_categories, fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match:
    return fc & fc2  # check whether sets overlap


pg_database = PostgreSQLSource(name="CLOUD_DB")
pg_database.with_table(name="users", features=User)
pg_database.with_table(name="sellers", features=Seller)

if __name__ == "__main__":
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
