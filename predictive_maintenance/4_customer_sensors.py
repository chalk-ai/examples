from chalk import batch
from chalk.features import DataFrame, features, has_many, feature
from chalk.sql import SnowflakeSource


@features
class Sensor:
    id: str
    customer_id: str
    is_failing: bool



@features
class Customer:
    id: str
    customer_needs_service: bool = feature(max_staleness="2h")
    sensors: DataFrame[Sensor] = has_many(lambda: Customer.id == Sensor.customer_id)


snowflake = SnowflakeSource()


@batch(cron="1h")
def get_sensors() -> DataFrame[Sensor.id, Sensor.customer_id, Sensor.is_failing]:
    """
    Incrementally ingest new sensors from our Snowflake warehouse
    as they become available.
    """
    return snowflake.query_string(
        """
        select id, customer_id, is_failing from sensors
        """
    ).incremental(incremental_column="updated_at", mode='row')


@batch(cron="1h")
def get_customers_needing_service(
    bad_sensors: Customer.sensors[
        Sensor.is_failing is True,
        Sensor.id
    ]
) -> Customer.customer_needs_service:
    return len(bad_sensors) > 0
