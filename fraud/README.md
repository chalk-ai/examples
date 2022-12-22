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

**[2_patterhs.py](2_patterns.py)**

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
## BELOW THIS IS A LIE

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