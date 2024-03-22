# E-commerce

Chalk can help you build realtime recommendation systems.

This guide shows you how to:
1). Implement User and Seller features in Chalk,
2). Add an Interaction feature and connect it to users,
3). Stream Interaction data from a Kafka queue.

In each section, you can find an `example_query.py` file. The file shows how the Chalk python client API can be used to
get information on the affinity between a User and a Seller.

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
