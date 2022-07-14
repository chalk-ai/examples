# Migrations
Migrations

https://docs.chalk.ai/docs/resolver-cron

## 1. Cron
Run resolvers on a schedule with all possible arguments.

**[1_cron.py](1_sampling.py)**

```python
@realtime(cron="30d")
def get_fico_score(name: User.name, email: User.email) -> User.fico_score:
    return ...
```
https://docs.chalk.ai/docs/resolver-cron

