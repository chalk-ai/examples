# DataFrames
A Chalk DataFrame is a 2-dimensional data structure similar 
to `pandas.Dataframe`, but with richer types and
underlying optimizations. 

https://docs.chalk.ai/docs/dataframe

## 1. Creating DataFrames
Describe features at a feature class or feature level.

**[1_creating_dataframes.py](1_creating_dataframes.py)**

```python
df = DataFrame.empty()
DataFrame.from_dict({
    User.id: [1, 2],
    User.email: ["elliot@chalk.ai", "samantha@chalk.ai"],
})
```
https://docs.chalk.ai/docs/dataframe

## 2. Filters
Filter the rows of a `DataFrame` by supplying conditions
to the `__getitem__()` method.

**[2_filtering.py](2_filters.py)**

```python
User.txns[
    Transaction.amount < 0,
    Transaction.merchant in {"uber", "lyft"} or Transaction.memo == "uberpmts",
    Transaction.canceled_at is None
]
```
https://docs.chalk.ai/docs/dataframe

## 3. Projections
Scope down the set of rows available in a `DataFrame`.

**[3_projections.py](3_projections.py)**

```python
User.txns[
    Transaction.amount,
    Transaction.memo
]
```
https://docs.chalk.ai/docs/dataframe

## 4. Projections with Filters
Compose projections and filters to create a new `DataFrame`.

**[4_filters_and_projections.py](4_filters_and_projections.py)**

```python
User.transactions[Transaction.amount > 100, Transaction.memo]
```

https://docs.chalk.ai/docs/dataframe#composing-projections-and-filters

## 5. Aggregations

Compute aggregates over a `DataFrame`.

**[5_aggregations.py](5_aggregations.py)**

```python
User.transactions[Transaction.amount].sum()
User.transactions[Transaction.amount].mean()
User.transactions[Transaction.amount].count()
User.transactions[Transaction.amount].max()
```
https://docs.chalk.ai/docs/dataframe#aggregations
