from datetime import datetime, timedelta

from chalk.client import ChalkClient
from chalk.features import DataFrame, has_many, feature_time, features, FeatureTime


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


ChalkClient().offline_query(
    input=labels[[Measurement.device_id]],
    input_times=[(datetime.now() - timedelta(days=30)).isoformat()],
    output=[Measurement.lat, Measurement.long, Measurement.temp],
)
