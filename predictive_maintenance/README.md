# Predictive Maintenance

Predicting device failure requires complex analysis executed 
against a variety of data sources. Chalk's platform allows 
data scientists to bring all the different data together, 
including streaming data from devices.

## 1. Device Data
Easily listen to streaming data and parse messages with 
custom logic.

**[1_device_data.py](1_device_data.py)**

```python
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
```
https://docs.chalk.ai/docs/streams

## 2. Historical Data
Access historical data as-of any time in the past

**[2_time_query.py](2_time_query.py)**

```python
ChalkClient.get_training_dataframe(
    input=labels[[Measurement.device_id]],
    input_times = [(datetime.now() - timedelta(days = 30)).isoformat()],
    output=[
        Measurement.lat,
        Measurement.long,
        Measurement.temp
    ]
)
```

https://docs.chalk.ai/docs/temporal-consistency

## 3. Sensor Streams

Compute streaming window aggregate functions
on sensor data.

**[3_keep_data_fresh.py](3_keep_data_fresh.py)**

```python
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
```

https://docs.chalk.ai/docs/aggregations

## 4. Failing Sensors

Combine batch, caching, and DataFrames to create a powerful
predictive maintenance pipeline.

**[4_customer_sensors.py](4_customer_sensors.py)**

```python
@batch(cron="1h")
def get_customers_needing_service(
    bad_sensors: Customer.sensors[
        Sensor.is_failing is True,
        Sensor.id
    ]
) -> Customer.customer_needs_service:
    return len(bad_sensors) > 0
```

https://docs.chalk.ai/docs/feature-caching
