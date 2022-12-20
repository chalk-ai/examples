# Caching
When a feature is expensive or slow to compute, 
you may wish to cache its value. 
Chalk uses the terminology "maximum staleness" 
to describe how recently a feature value needs 
to have been computed to be returned without 
re-running a resolver.

https://docs.chalk.ai/docs/feature-caching

## 1. Basic Caching
Cache feature values rather than computing them realtime.

**[1_basic_caching.py](1_basic_caching.py)**

```python
@features
class User:
    fico_score: int = feature(max_staleness="30d")
```
https://docs.chalk.ai/docs/feature-caching

## 2. Latest Computed Value
Pull the last computed example of the feature before
looking for a resolver to run.

**[2_latest_value.py](2_lastest_value.py)**

```python
@features
class User:
    fico_score: int = feature(max_staleness="infinity")
```
https://docs.chalk.ai/docs/feature-caching

## 3. Intermediate Feature Values
Caching also works when features are needed as intermediate
results.

**[3_intermediates.py](3_intermediates.py)**

```python
ChalkClient().query(
    input={ ... },
    # User.fico_score is not requested in the output...
    output=[User.risk_score],
    # ...but you can specify the staleness anyhow!
    staleness={User.fico_score: "10m"},
)
```
https://docs.chalk.ai/docs/query-caching

## 4. Overriding Max-Staleness
Setting max-staleness at the time of making a feature request.

**[4_override_max_staleness.py](4_override_max_staleness.py)**

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
https://docs.chalk.ai/docs/query-caching

## 5. Overriding Cache Values
Supply a feature value in the input to skip the cache and any resolver entirely.

**[5_override_cache_values.py](5_override_cache_values.py)**

```python
@features
class User:
    fico_score: int = feature(max_staleness="30d")

ChalkClient().query(
    input={User.fico_score: 1, ...},
    output=[...],
)
```
https://docs.chalk.ai/docs/query-caching

## 6. Cache Busting
Bypass the cache with a max-staleness of 0.

**[6_cache_busting.py](6_cache_busting.py)**

```python
ChalkClient().query(
    input={...},
    output=[User.fico_score],
    staleness={User.fico_score: "0s"},
)
```
https://docs.chalk.ai/docs/query-caching#cache-busting


## 7. Pre-Fetching
Keep the cache warm by scheduling a resolver to run
more frequently than the max-staleness.

**[7_prefetching.py](7_prefetching.py)**

```python
@features
class User:
    fico_score: int = feature(max_staleness="30d")

@realtime(cron="29d 11h")
def get_fico_score(name: User.name) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
```
https://docs.chalk.ai/docs/resolver-cron

