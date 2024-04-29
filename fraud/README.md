# Fraud Detection

Finding a balance between user experience and
risk management is a complex task for banking
products. Chalk helps you express complex business
logic with features and resolvers, and lets data
scientists and machine learning engineers collaborate
on solutions.

## 1. Returns

Identify transactions returned for non-sufficient funds.

**[1_return.py](1_return.py)**

```python
@online
def get_transaction_is_nsf(
    memo_clean: Transaction.clean_memo,
) -> Transaction.is_nsf:
    return "nsf" in memo_clean.lower()

@online
def get_nsf_amount(
    amounts: User.transactions[
        Transaction.is_nsf is True,
        Transaction.amount
    ]
) -> User.nsf_amount:
    return amounts.sum()
```

https://docs.chalk.ai/docs/resolver-inputs

## 2. Changes in Behavior

Detect changes in user behavior over time.

**[2_patterns.py](2_patterns.py)**

```python
@online
def get_transaction_trend(
    this_year_txns: User.transactions[after(days_ago=30)],
    last_year_txns: User.transactions[
        before(days_ago=30),
        after(days_ago=30 * 2)
    ]
) -> User.change_from_last_year:
    sum_last = last_year_txns[Transaction.amount].sum()
    sum_this = this_year_txns[Transaction.amount].sum()
    return (sum_last - sum_this) / sum_last
```

https://docs.chalk.ai/docs/window-functions

## 3. Identity Verification

Make use of vendor APIs to verify identities, control costs with Chalk's platform.

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

## 4. Withdrawal Model

Decide and enforce withdrawal limits with custom hold times.

**[4_withdrawal_model.py](4_withdrawal_model.py)**

```python
@realtime(when=TransferLimit.to_account.is_internal is False)
def withdrawal_limit(
        internal_accounts: TransferLimit.user.accounts[Account.is_internal is True],
        deposits_last_90: TransferLimit.user.transfers[Transfer.from_account.is_internal is False, before(days_ago=90)],
        user_settlement: TransferLimit.user.holdback,
) -> TransferLimit.amount:
    ...
```

https://docs.chalk.ai/docs/resolver-overview

## 5. Account Takeover

Aggregate failed logins over a Kafka stream.

**[5_account_takeover.py](5_account_takeover.py)**

```python
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

https://docs.chalk.ai/docs/aggregations
