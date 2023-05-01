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
    distinct_ips: Windowed[int] = windowed("10m", "30m", "1d")


class LoginMessage(BaseModel):
    user_id: int
    failed: bool
    ip_address: int


@stream(source=src, mode='continuous')
def failed_logins(events: DataFrame[LoginMessage]) -> DataFrame[
    User.id,
    User.distinct_ips
]:
    return f"""
        select
          user_id as id,
          approximate_count_distinct(id_address) as distinct_ips
        from {events}

    """
