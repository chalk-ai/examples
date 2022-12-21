# Transaction Enrichment
Chalk can help you build insight into the financial transactions
of your users.

## 1. Income
Compute income from Plaid transactions.

**[1_income.py](1_income.py)**

```python
@realtime
def get_plaid_income(
    txns: User.plaid_transactions[
        PlaidTransaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    return -txns[PlaidTransaction.amount].sum()
```

https://docs.chalk.ai/docs/features

## 2. Income
Compute income from Plaid transactions.

**[1_income.py](1_income.py)**

```python
@realtime
def get_plaid_income(
    txns: User.plaid_transactions[
        PlaidTransaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    return -txns[PlaidTransaction.amount].sum()
```

https://docs.chalk.ai/docs/features
## 1. Income
Compute income from Plaid transactions.

**[1_income.py](1_income.py)**

```python
@realtime
def get_plaid_income(
    txns: User.plaid_transactions[
        PlaidTransaction.is_payroll is True,
        after(days_ago=30),
    ],
) -> User.computed_income_30:
    return -txns[PlaidTransaction.amount].sum()
```

https://docs.chalk.ai/docs/features
