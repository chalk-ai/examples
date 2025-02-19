# Examples

Curated examples and patterns for using Chalk. Use these to build your feature pipelines.

## [1_features](01_features)

Declare and version features from Python.

```python
@features(owner="librarians@sfpl.org")
class Author:
    id: str
    # The Author's email
    # :tags: pii
    name: str
    nickname: str | None
    books: DataFrame[Book] = has_many(lambda: Book.author_id == Author.id)

@features
class Book:
    id: str
    author_id: str
```

## [2_resolvers](02_resolvers)

Resolvers are Python functions that compute your feature values.
They take as input features that they need to know to run,
and resolve the values of one or more features. In both cases,
you use Python type annotations to define these dependencies and
outputs.

```python
@online
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()

@online
def is_banned_email(domain: User.email_domain) -> User.banned_email:
    return domain in {"pergi.id", ...}
```

https://docs.chalk.ai/docs/resolver-overview

## [3_caching](03_caching)

When a feature is expensive or slow to compute,
you may wish to cache its value.
Chalk uses the terminology "maximum staleness"
to describe how recently a feature value needs
to have been computed to be returned without
re-running a resolver.

https://docs.chalk.ai/docs/feature-caching

```python
@features
class User:
    fico_score: int = feature(max_staleness="30d")

ChalkClient().query(
    input={...},
    output=[User.fico_score],
    staleness={User.fico_score: "10m"},
)
```

https://docs.chalk.ai/docs/feature-caching

## [4_scheduling](04_scheduling)

Run resolvers on a schedule, sampling values
for the inputs.

```python
def only_active_filter(last_login: User.last_login, status: User.status) -> bool:
    return status == "active" and last_login > datetime.now() - timedelta(days=30)

@realtime(cron=Cron(schedule="29d 11h", filter=only_active_filter))
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
```

https://docs.chalk.ai/docs/resolver-cron

## [5_feature_discovery](05_feature_discovery)

Capture metadata to inform alerting, monitoring, and discovery.

```python
@features(owner="shuttle@nasa.gov", tags="group:rocketry")
class SpaceShuttle:
    id: str

    # The SHA1 of the software deployed to the shuttle.
    # Should align with a git commit on main.
    #
    # :owner: katherine.johnson@nasa.gov
    software_version: str

    # The volume of this shuttle in square meters.
    # :owner: architecture@nasa.gov
    # :tags: zillow-fact, size
    volume: str
```

https://docs.chalk.ai/docs/feature-discovery

## [6_dataframe](06_dataframe)

A Chalk DataFrame is a 2-dimensional data structure similar
to `pandas.Dataframe`, but with richer types and
underlying optimizations.

```python
User.txns[
    Transaction.amount < 0,
    Transaction.merchant in {"uber", "lyft"} or Transaction.memo == "uberpmts",
    Transaction.canceled_at is None,
    Transaction.amount
].sum()
```

https://docs.chalk.ai/docs/dataframe

## [7_streaming](07_streaming)

Chalk gives a simple way to express streaming computations,
for both mapping stream and window aggregate streams.

```python
@stream(...)
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

https://docs.chalk.ai/docs/streams

https://docs.chalk.ai/docs/aggregations

## [8_testing](08_testing)

Test your Chalk features and resolvers.

```python
@realtime
def get_home_data(
        hid: HomeFeatures.id,
) -> Features[HomeFeatures.price, HomeFeatures.sq_ft]:
    return HomeFeatures(price=200_000, sq_ft=2_000)

def test_multiple_output():
    assert get_home_data(2) == HomeFeatures(
        price=200_000,
        sq_ft=2_000,
    )
```

https://docs.chalk.ai/docs/unit-tests

## [9_github_actions](09_github_actions)

Deploy feature pipelines in GitHub Actions.

Docs: https://docs.chalk.ai/docs/github-actions

CLI Step: https://github.com/chalk-ai/cli-action

Deploy Step: https://github.com/chalk-ai/deploy-action

```yaml
- uses: chalk-ai/deploy-action@v2
  with:
    client-id: ${{secrets.CHALK_CLIENT_ID}}
    client-secret: ${{secrets.CHALK_CLIENT_SECRET}}
    await: true
    no-promote: true
```

## [10_migrations](10_migrations)

Docs on migrations coming soon!

## [11_sql](11_sql)

Chalk can ingest your data using a SQL interface
from any of the integrations that support it.
You can describe your queries using SQL strings
or [SQLAlchemy](https://www.sqlalchemy.org/).

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

## [credit](credit)

Chalk can help you build insight into the financial transactions
of your users.

```python
@realtime
def tradeline_rollup(
        accounts: User.tradelines[
            Tradeline.is_delinquent is True
            ]
) -> User.delinquent_amount:
    return accounts[Tradeline.outstanding].sum()
```

http://chalk.ai/solutions/credit

## [fraud](fraud)

Finding a balance between user experience and
risk management is a complex task for banking
products. Chalk helps you express complex business
logic with features and resolvers, and lets data
scientists and machine learning engineers collaborate
on solutions.

```python
@realtime(when=TransferLimit.to_account.is_internal is False)
def withdrawal_limit(
        internal_accounts: TransferLimit.user.accounts[Account.is_internal is True],
        deposits_last_90: TransferLimit.user.transfers[Transfer.from_account.is_internal is False, before(days_ago=90)],
        user_settlement: TransferLimit.user.holdback,
) -> TransferLimit.amount:
    ...

@stream(...)
def agg_logins(df: DataFrame[LoginMessage]) -> DataFrame[User]:
    return f"""
        select
            count(*) as failed_logins,
            user_id as id
        from {df}
        where status = 'failed'
        group by id
    """
```

http://chalk.ai/solutions/fraud

## [predictive_maintenance](predictive_maintenance)

Predicting device failure requires complex analysis executed
against a variety of data sources. Chalk's platform allows
data scientists to bring all the different data together,
including streaming data from devices.

```python
@stream(...)
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

http://chalk.ai/solutions/maintenance
