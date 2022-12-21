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
    return txns[PlaidTransaction.amount].sum()
```

https://docs.chalk.ai/docs/features

## 2. Multiple Accounts
Identify users with multiple accounts.

**[2_accounts.py](2_accounts.py)**

```python
@features
class User:
    id                   : str
    name                 : str
    accounts             : DataFrame[BankAccount] 
        = has_many(lambda: BankAccount.userName 
                           == User.name)
    number_of_accounts   : int

```

https://docs.chalk.ai/docs/has-many

## 3. Credit Bureau API
Integrate data from credit bureaus like Equifax

**[3_bureau_api.py](3_bureau_api.py)**

```python
def get_credit_report(first_name: User.first_name, last_name: User.last_name,
                      city: User.city, state: User.state, id = User.id
    ) -> CreditReport:
    args = {
        "firstName": first_name,
        "lastName": last_name,
        "city": city,
        "state": state
        }
    res = requests.post(f"{url}/equifax/credit-report", args).json()

    return CreditReport(
        user_id=id, 
        report_id=res["pdfReportId"], 
        report=res["data"]
    )

```

https://docs.chalk.ai/docs/resolver-overview