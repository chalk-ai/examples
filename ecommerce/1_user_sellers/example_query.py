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
        output=[UserSeller.user.id, UserSeller.seller.id, UserSeller.favorites_match],
    )
    print(user_stores)
