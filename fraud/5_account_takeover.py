from enum import Enum
from pydantic import BaseModel

from chalk.features import (
    DataFrame,
    features,
)
from chalk.streams import KafkaSource, stream, windowed, Windowed


@features
class User:
    id: str
    failed_logins: Windowed[int] = windowed("10m", "30m", "1h")


source = KafkaSource(name="sensor_stream")


class LoginStatus(Enum):
    success = "success"
    failed = "failed"


class LoginMessage(BaseModel):
    user_id: str
    status: LoginStatus


@stream(source=source, mode="continuous")
def agg_logins(df: DataFrame[LoginMessage]) -> DataFrame[User]:
    return f"""
        select
            count(*) as failed_logins,
            user_id as id
        from {df}
        where status = 'failed'
        group by id
    """
