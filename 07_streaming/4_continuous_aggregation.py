from pydantic import BaseModel

from chalk import stream
from chalk.features import DataFrame, Features, features
from chalk.streams import KafkaSource
from chalk.streams import Windowed, windowed

src = KafkaSource(
    bootstrap_server='kafka.website.com:9092',
    topic='user_favorite_color_updates'
)


@features
class User:
    id: str
    num_failed_logins: Windowed[int] = windowed("10m", "30m", "1d")


class LoginMessage(BaseModel):
    user_id: int
    success: bool


@stream(source=src, mode='continuous', keys={"user_id": User.id})
def failed_logins(events: DataFrame[LoginMessage]) -> Features[
    User.id,
    User.num_failed_logins
]:
    return User(id=events[0].user_id, num_failed_logins=sum(1 for e in events if e.success))
