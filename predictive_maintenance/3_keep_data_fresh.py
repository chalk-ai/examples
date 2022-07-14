from datetime import datetime
from pydantic import BaseModel

from chalk.features import DataFrame, features
from chalk.streams import stream, KafkaSource, Windowed, windowed


@features
class Sensor:
    id: str
    count_failed: Windowed[int] = windowed("10m", "20m")


source = KafkaSource(name="sensor_stream")


class Message(BaseModel):
    device_id: str
    timestamp: datetime
    is_failing: bool


@stream(source=source, mode="continuous")
def process_measurements(df: DataFrame[Message]) -> DataFrame[Sensor]:
    return f"""
        select
            count(*) as count_failed,
            id as device_id
        from {df}
        where is_failing <> TRUE
        group by id
    """
