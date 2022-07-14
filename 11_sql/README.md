# SQL

Chalk can ingest your data using a SQL interface from any 
of the integrations that support it. You can describe your 
queries using SQL strings or SQLAlchemy. In offline, event 
tables can be ingested incrementally.

https://docs.chalk.ai/docs/sql

## 1. Query Scalars
Query scalars with SQL files or strings.

**[1_scalars.py](1_scalars.py)**

```python
@realtime
def get_views(user: User.id) -> User.viewed_minutes:
    return db.query_string(
        "select sum(mins) as viewed_minutes from view_counts where uid = :uid",
        args=dict(uid=user),
    ).one()
```
https://docs.chalk.ai/docs/sql

## 2. Query DataFrames
Query many rows and take advantage of push down filters.

**[2_dataframes.py](2_dataframes.py)**

```python
@realtime
def get_views() -> DataFrame[User]:
    return db.query_string(
        """
        select id, sum(mins) as viewed_minutes 
        from view_counts 
        group by id
        """,
    ).all()
```

https://docs.chalk.ai/docs/sql
