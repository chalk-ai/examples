# Feature Discovery
Capture metadata to inform alerting, monitoring, and discovery.

https://docs.chalk.ai/docs/feature-discovery

## 1. Descriptions
Describe features at a feature class or feature level.

**[1_descriptions.py](1_descriptions.py)**

```python
@features
class RocketLaunch:
    # Feature descriptions are parsed from your code!
    launched_at: datetime
```
https://docs.chalk.ai/docs/feature-discovery#description

## 2. Owners
Assign owners to features.

**[2_owners.py](2_owners.py)**

```python
@features(owner="default-owner@gmail.com")
class RocketLaunch:
    # :owner: specific-owner@gmail.com
    launched_at: datetime
```
https://docs.chalk.ai/docs/feature-discovery#owner

## 3. Tags
Tag related features.

**[3_tags.py](3_tags.py)**

```python
@features(tags="group:risk")
class RiskReport:
    id: str
    risk_score: str
    # :tags: pii
    first_name: str
```
https://docs.chalk.ai/docs/feature-discovery#tags

## 4. Unified
Overview of all of the above.

**[4_unified.py](4_unified.py)**

```python
@features(owner="shuttle@nasa.gov", tags="group:rocketry")
class SpaceShuttle:
    # The volume of this shuttle in square meters.
    # :owner: architecture@nasa.gov
    # :tags: zillow-fact, size
    volume: str

assert tags(SpaceShuttle.volume) == ["zillow-fact", "size", "group:rocketry"]
```
