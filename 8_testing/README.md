# Testing
Testing for Chalk resolvers.

## 1. Unit tests
Resolvers are just Python functions, so they are easy to unit test.

Chalk lets you specify your feature pipelines using
idiomatic Python. This means that you can unit test
individual resolvers and combinations of resolvers.

**[1_unit_tests.py](1_unit_tests.py)**

```python
@realtime
def get_home_data(
        hid: HomeFeatures.id,
) -> Features[HomeFeatures.price, HomeFeatures.sq_ft]:
    return HomeFeatures(price=200_000, sq_ft=2_000)


def test_multiple_output():
    assert get_home_data(2) == HomeFeatures(
        price=200_000,
        sq_ft=2_000,
    )
```
https://docs.chalk.ai/docs/unit-tests

## 2. Integration tests
Use preview deployments to integration test interactions
between resolvers.

**[2_integration_tests.py](2_integration_tests.py)**

```bash
> chalk apply --no-promote
```

```bash
> chalk query --deployment $DEPLOYMENT_ID \
              --in user.id=1 \
              --out user.id \
              --out user.email
```
https://docs.chalk.ai/docs/integration-tests
