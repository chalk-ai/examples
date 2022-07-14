# Scheduling
Automate resolver runs.

https://docs.chalk.ai/docs/resolver-cron

## 1. Cron
Run resolvers on a schedule with all possible arguments.

**[1_cron.py](1_cron.py)**

```python
@realtime(cron="30d")
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return ...
```
https://docs.chalk.ai/docs/resolver-cron

## 2. Filtered Cron
Run resolvers on a schedule and filter down which examples to consider.

**[2_filtered_cron.py](2_filtered_cron.py)**

```python
def only_active_filter(last_login: User.last_login, status: User.status) -> bool:
    return status == "active" and last_login > datetime.now() - timedelta(days=30)

@realtime(cron=Cron(schedule="29d 11h", filter=only_active_filter))
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
```
https://docs.chalk.ai/docs/resolver-cron#filtering-examples

## 3. Sampling Cron
Pick exactly the examples that you’d like to run.

**[3_sample_arguments.py](3_sample_arguments.py)**

```python
def get_active_users() -> DataFrame[User.id]:
    return session.query_string(
        "select users.id from users where users.active = true",
        fields={"id": User.id},
    ).all()

@realtime(cron=Cron(schedule="29d 11h", sample=get_active_users))
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return requests.get("https://experian.com").json()["score"]
```
https://docs.chalk.ai/docs/resolver-cron#custom-examples
