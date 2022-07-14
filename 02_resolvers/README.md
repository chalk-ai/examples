# Resolvers
Resolvers are Python functions that compute your feature values. 
They take as input features that they need to know to run, 
and resolve the values of one or more features. In both cases, 
you use Python type annotations to define these dependencies and 
outputs.

https://docs.chalk.ai/docs/resolver-overview

## 1. Scalar Resolvers
Create a resolver that returns a single feature.

**[1_scalar_resolver.py](1_scalar_resolver.py)**

```python
@realtime
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()

ChalkClient().query(
    input={User.email: "jessie@chalk.ai"},
    output=[User.email_domain],
)
```
https://docs.chalk.ai/docs/resolver-overview

## 2. Multi-Feature Resolvers
Create a resolver that returns many features.

**[2_multiple_features_resolver.py](2_multiple_features_resolver.py)**

```python
@realtime
def get_email_info(id: User.id) -> Features[User.email_domain, User.email]:
    return User(
        email="katherine.johnson@nasa.gov", 
        email_domain="nasa.gov"
    )
```
https://docs.chalk.ai/docs/resolver-overview

## 3. Downstream Scalars
Resolvers chain together through their required dependencies
and declared outputs.

**[3_downstream_scalars.py](3_downstream_scalars.py)**

```python
@realtime
def get_email_domain(email: User.email) -> User.email_domain:
    return email.split("@")[1].lower()

@realtime
def is_banned_email(domain: User.email_domain) -> User.banned_email:
    return domain in DOMAIN_DENY_LIST

result = ChalkClient().query(
    input={User.email: "katherine.johnson@nasa.gov"},
    output=[User.banned_email],
)
```
https://docs.chalk.ai/docs/resolver-overview

## 4. Downstream DataFrames
Chain a DataFrame resolver with a scalar resolver.

**[4_downstream_dataframes.py](4_downstream_dataframes.py)**

```python
@realtime
def banned_user(domains: User.emails[Email.is_banned is True]) -> User.banned:
    return len(domains) > 0
```
https://docs.chalk.ai/docs/resolver-overview

## 5. Tagged Resolvers
Trigger special behavior with tags.

**[5_tagged_resolvers.py](5_tagged_resolvers.py)**

```python
@realtime(tags="mock")
def mock_check_banned_email(domain: User.email_domain) -> User.banned_email:
    if domain == "chalk.ai":
        return False
    if domain == "fraudster.com":
        return True
    return random() < 0.1

@realtime
def check_banned_email(score: User.email_risk_score) -> User.banned_email:
    return score >= 0.8
```
https://docs.chalk.ai/docs/resolver-overview

## 6. Sharing Resolvers
Resolvers are shared between all models.

**[6_sharing_resolvers.py](6_sharing_resolvers.py)**

```python
ChalkClient().query(
    input={User.id: 1},
    output=[
        User.emails_sent_last_10_days,
        User.name,
    ],
    query_name="send_reminder_email",
)
ChalkClient().query(
    input={Loan.id: 1},
    output=[
        Loan.user.emails_sent_last_10_days,
        Loan.amount,
    ],
    query_name="expected_loan_repayment",
)
```
https://docs.chalk.ai/docs/resolver-overview

## 7. Multi-Tenancy
Serve many end-customers with differentiated behavior.

**[7_multi_tenancy.py](7_multi_tenancy.py)**

```python
@online(environment="disney")
def get_disney_sessions_for_user(
    u: User.id,
) -> WatchSession.duration:
    return ...

@online(environment="hbo")
def get_hbo_sessions_for_user(
        u: User.id,
) -> WatchSession.duration:
    return ...
```
https://docs.chalk.ai/docs/resolver-overview
