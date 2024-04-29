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

    # Chalk make it easy to calculate time windowed features,
    # below we calculate the number of failed logins in the
    # past 10 minutes, 30 minutes, and 1 hour.
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
    # If a resolver returns a dataframe and takes a dataframe,
    # but the function returns a string, Chalk treats the return
    # value as a SQL query, which it will execute on the passed
    # in dataframe
    return f"""
        select
            count(*) as failed_logins,
            user_id as id
        from {df}
        where status = 'failed'
        group by id
    """
