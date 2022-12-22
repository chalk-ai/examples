# Fraud Detection
Chalk's platform helps you 

## 1. Returns
Identify transactions returned for non-sufficient funds

**[1_return.py](1_return.py)**

```python
@realtime
def get_transaction_is_nsf(
        memo_clean: PlaidTransaction.clean_memo,
) -> PlaidTransaction.is_nsf:
    return "nsf" in memo_clean.lower()

@realtime
def get_nsf_amount(amounts: User.plaid_transactions[
    PlaidTransaction.is_nsf is True,
    PlaidTransaction.amount]) -> User.nsf_amount:
    return amounts.sum()

```
https://docs.chalk.ai/docs/resolver-inputs

## 2. Changes in behavior
Identify changes in user behavior over time

**[2_patterns.py](2_patterns.py)**

```python
@realtime
def get_transaction_trend(this_year_txns: User.transactions[after(days_ago=30)],
                          last_year_txns: User.transactions[before(years_ago=1), after(years_ago=1, days_ago=30)]
                          ) -> User.change_from_last_year:
    sum_last = last_year_txns['amount'].sum()
    sum_this = this_year_txns['amount'].sum()
    return (sum_last - sum_this) / sum_last


```

https://docs.chalk.ai/docs/window-functions

## 3. Identity Verification

**[3_identity.py](3_identity.py)**

```python
@features
class User:
    id: str
    socure_score: float = feature(max_staleness="30d")

@online
def get_socure_score(uid: User.id) -> Features[User.socure_score]:
    return (
        requests.get("https://api.socure.com", json={
            id: uid
        }).json()['socure_score']
    )

```

https://docs.chalk.ai/docs/feature-caching