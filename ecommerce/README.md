# E-commerce

Chalk can help you build realtime recommendation systems

## 1. Set up and query Users & Sellers

**[1_users_sellers.py](1_user_sellers.py)**

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

## 2. Add User Seller Interactions

Add user-seller interactions and update user-seller ranking.

- features: **[2_interactions](2_interactions/features.py)**
- resolvers: **[2_interactions](2_interactions/resolvers.py)**
- datasources: **[2_interactions](2_interactions/datasources.py)**

### features.py

Add interactions feature

```python
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

- features: **[3_interactions/features.py](2_interactions/features.py)**
- resolvers: **[3_interactions/resolvers.py](2_interactions/resolvers.py)**
- models: **[3_interactions/models.py](2_interactions/models.py)**
- datasources: **[3_interactions/datasources.py](2_interactions/datasources.py)**

```python

```
