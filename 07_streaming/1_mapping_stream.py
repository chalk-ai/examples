from pydantic import BaseModel

from chalk import stream
from chalk.features import Features, features
from chalk.streams import KafkaSource


@features
class User:
    id: str
    favorite_color: str


class UserUpdateBody(BaseModel):
    user_id: str
    favorite_color: str


src = KafkaSource(
    bootstrap_server='kafka.website.com:9092',
    topic='user_favorite_color_updates'
)


@stream(source=src)
def fn(message: UserUpdateBody) -> Features[User.id, User.favorite_color]:
    return User(
        id=message.user_id,
        favorite_color=message.favorite_color,
    )
