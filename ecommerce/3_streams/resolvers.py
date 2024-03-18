from chalk.features import Features
from chalk import stream, online
from features import UserSeller, Interaction, InteractionKind
from datasources import interaction_stream
from models import InteractionMessage
import uuid


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
    fc: UserSeller.user.favorite_categories,
    fc2: UserSeller.seller.categories
) -> UserSeller.favorites_match:
    return fc & fc2 # check whether sets overlap
