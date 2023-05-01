# Streaming

Chalk ships with a powerful streams module for computing
features from a stream and computing window functions
on streams.

https://docs.chalk.ai/docs/streams

https://docs.chalk.ai/docs/aggregations

## 1. Mapping Stream
Create features directly from messages on a stream.

**[1_mapping_stream.py](1_mapping_stream.py)**

```python
@stream(source=src)
def fn(message: UserUpdateBody) -> Features[User.uid, User.favorite_color]:
    return User(
        uid=message.value.user_id,
        favorite_color=message.value.favorite_color
    )
```

https://docs.chalk.ai/docs/streams

## 2. Stream DataFrame

Compute a streaming window aggregate function using [DataFrames](https://docs.chalk.ai/docs/dataframe).

**[2_window_dataframe.py](2_window_dataframe.py)**

```python
@stream(source=src)
def failed_logins(events: DataFrame[LoginMessage]) -> Features[
    User.id,
    User.num_failed_logins
]:
    return User(
        id=events["id"].max(),
        num_failed_logins=events["failed"].sum(),
    )
```

https://docs.chalk.ai/docs/aggregations#using-dataframes

## 3. Stream SQL

Compute a streaming window aggregate function using [DataFrames](https://docs.chalk.ai/docs/dataframe).

**[3_window_sql.py](3_window_sql.py)**

```python
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
```

https://docs.chalk.ai/docs/aggregations#using-sql

## 4. Stream SQL Aggregation

Compute an aggregation on windows using [DataFrames](https://docs.chalk.ai/docs/dataframe).

**[4_continuous_sql.py](4_continuous_sql.py)**

```python
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
```
