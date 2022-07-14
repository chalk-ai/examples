# Examples

Curated examples and patterns for using Chalk. Use these to build your feature pipelines.

## [1_features](1_features)

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
```

## [2_resolvers](2_resolvers)

Define the computation for computing feature values.

```python
@realtime
def get_something():
    pass
```

## [3_caching](3_caching)

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

## [5_feature_discovery](5_feature_discovery)

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

## [9_github_actions](9_github_actions)

Deploy feature pipelines in GitHub Actions.

https://docs.chalk.ai/docs/github-actions

```yaml
- uses: chalk-ai/deploy-action@v1
  with:
    client-id: ${{secrets.CHALK_CLIENT_ID}}
    client-secret: ${{secrets.CHALK_CLIENT_SECRET}}
    await: true
    no-promote: true
```
