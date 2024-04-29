# Credit

Chalk can help you build insight into the financial transactions
of your users.

## 1. Income

Compute income from Plaid transactions.

**[1_income.py](1_income.py)**

```python
@realtime
def get_plaid_income(
        txns: User.transactions[
            PlaidTransaction.is_payroll is True,
            after(days_ago=30),
        ],
) -> User.computed_income_30:
    return txns[PlaidTransaction.amount].sum()
```

https://docs.chalk.ai/docs/features

## 2. Multiple Accounts

Identify users with multiple accounts.

**[2_accounts.py](2_accounts.py)**

```python
@features
class Account:
  id: int
  user_id: "User.id"
  user: "User"

@features
class User:
    id: int
    accounts: DataFrame[Account]
```

https://docs.chalk.ai/docs/has-many

## 3. Credit Bureau API

Integrate data from credit bureaus like Transunion.

**[3_bureau_api.py](3_bureau_api.py)**

```python
@realtime
def get_credit_report(
    first_name: User.first_name,
    last_name: User.last_name,
    city: User.city,
    state: User.state,
    id: User.id,
) -> CreditReport:
    res = requests.post(
        f"{url}/transunion/credit-report",
        json={
            "firstName": first_name,
            "lastName": last_name,
            "city": city,
            "state": state,
        },
    ).json()
    return CreditReport(user_id=id, report_id=res["pdfReportId"], report=res["data"])
```

https://docs.chalk.ai/docs/resolver-overview

## 4. Aggregate Tradelines

Aggregate user statistics across tradelines.

**[4_aggregate_tradelines.py](4_aggregate_tradelines.py)**

```python
@realtime
def tradeline_rollup(
    accounts: User.tradelines[
        Tradeline.is_delinquent is True
    ]
) -> User.delinquent_amount:
    return accounts[Tradeline.outstanding].sum()
```

https://docs.chalk.ai/docs/resolver-overview
