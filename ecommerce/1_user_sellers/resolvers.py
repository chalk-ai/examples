from chalk import online
from models import UserSeller

@online
def get_similarity(
    fc: UserSeller.user.favorite_categories,
    fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match:
    return fc & fc2 # check whether sets overlap
