# Resolvers
Resolvers are Python functions that compute your feature values. 
Resolvers take as input features that they need to know to run, 
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

## 2. Multiple Features Resolvers
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

## 3. Downstream Resolvers
Resolvers chain together through their required dependencies
and declared outputs.

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
