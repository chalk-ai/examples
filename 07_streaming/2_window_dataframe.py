from pydantic import BaseModel

from chalk import stream
from chalk.features import Features, DataFrame
from chalk.features import features
from chalk.streams import KafkaSource
from chalk.streams import Windowed, windowed


src = KafkaSource(
    bootstrap_server='kafka.website.com:9092',
    topic='user_favorite_color_updates'
)


@features
class User:
    id: str
    num_failed_logins: Windowed[int] = windowed("10m**", "30", "1d")


class LoginMessage(BaseModel):
    user_id: int
    failed: bool


@stream(source=src)
def failed_logins(events: DataFrame[LoginMessage]) -> Features[
    User.id,
    User.num_failed_logins
]:
    return User(
        id=events["id"].max(),
        num_failed_logins=events["failed"].sum(),
    )
