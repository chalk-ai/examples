from pydantic import BaseModel

from chalk import stream
from chalk.features import DataFrame
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
    num_failed_logins: Windowed[int] = windowed("10m", "30m", "1d")


class LoginMessage(BaseModel):
    user_id: int
    failed: bool


@stream(source=src)
def failed_logins(events: DataFrame[LoginMessage]) -> DataFrame[
    User.id,
    User.num_failed_logins
]:
    return f"""
        select
          user_id as id,
          count(*) as num_failed_logins
        from {events}
        where failed = 1
        group by 1
    """
