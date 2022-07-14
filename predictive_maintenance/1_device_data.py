from datetime import datetime
from pydantic import BaseModel

from chalk.features import DataFrame, has_many, features, FeatureTime
from chalk.streams import stream, KafkaSource


@features
class Measurement:
    device_id: str
    lat: float
    long: float
    voltage: float
    temp: float

    timestamp: FeatureTime


@features
class Sensor:
    id: str
    measurements: DataFrame[Measurement] = has_many(lambda: Measurement.device_id == Sensor.id)


source = KafkaSource(name="sensor_stream")


class DeviceDataJson(BaseModel):
    latitude: float
    longitude: float
    voltage: float
    temperature: float


class Message(BaseModel):
    device_id: str
    timestamp: datetime
    data: DeviceDataJson


@stream(source=source)
def read_message(message: Message) -> Measurement:
    return Measurement(
        device_id=message.device_id,
        timestamp=message.timestamp,
        lat=message.data.latitude,
        long=message.data.longitude,
        voltage=message.data.voltage,
        temp=message.data.temperature,
    )
