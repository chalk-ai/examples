# Setting Up and Querying Users & Sellers

Create Chalk features for Users and Sellers and evaluate whether a user and seller have accordant categories.

- features: **[1_user_sellers/features.py](./features.py)**
- resolvers: **[1_user_sellers/resolvers.py](./resolvers.py)**
- datasources: **[1_user_sellers/datasources.py](./datasources.py)**

## features.py

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

## resolvers.py

Create an online resolver that creates a favorites_match feature on UserSeller. This feature indicates whether a specific user and seller have overlapping categories.

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

## datasources.py

Create postgres datasource and resolve User and Seller from tables.

```python
from chalk.sql import PostgreSQLSource
from features import User, Seller

pg_database = PostgreSQLSource(name="CLOUD_DB")
pg_database.with_table(name="users", features=User)
pg_database.with_table(name="sellers", features=Seller)
```
