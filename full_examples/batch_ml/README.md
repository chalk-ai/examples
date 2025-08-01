# Batch Machine Learning Example With Chalk

This example demonstrates batch machine learning capabilities in Chalk, featuring fraud detection on transaction data with incremental processing and offline model execution.

## Overview

This project implements a fraud detection system that:
- Processes transaction data incrementally from Snowflake
- Runs daily batch predictions using an ONNX model (on new transactions)
- Stores results both online and offline for serving and analysis

## Key Features

### Incremental Data Processing

The transaction data is processed incrementally using Chalk's row-based incremental mode:

```sql
-- get transactions from snowflake
-- source: sf
-- resolves: Transaction
-- tag: ['model_sample']
-- incremental:
--   mode: row
--   lookback_period: 60m
--   incremental_column: ts
SELECT
    transaction_id as id,
    user_id,
    merchant_id,
    amount,
    ts,
    category
FROM
    "ML.TRANSACTIONS"
WHERE category <> "pending"
```

This configuration ensures only new transactions (based on the `ts` timestamp column) are processed, with a 60-minute lookback period to handle late-arriving data.

### Offline Batch Model Execution

The fraud detection model runs as a scheduled offline resolver:

```python
@offline
def run_fraud_model(
    features: DataFrame[
        Transaction.id,
        Transaction.amount,
        Transaction.user.time_since_last_transaction,
        Transaction.user.num_transactions["1d"],
        Transaction.user.num_transactions["10d"],
        Transaction.user.num_transactions["30d"],
        Transaction.user.num_distinct_merchants_transacted["1d"],
        Transaction.user.num_distinct_merchants_transacted["10d"],
        Transaction.user.num_distinct_merchants_transacted["30d"],
    ],
) -> DataFrame[Transaction.id, Transaction.is_fraud]:
    """Predict user churn based on transaction data."""

    predictions = fraud_model.predict(
        features.to_pandas().astype(np.float32).drop(columns=[Transaction.id]).values,
    )

    return features[Transaction.id].with_columns(
        {Transaction.is_fraud: predictions}
    )
```

This function is executed daily via a ScheduledQuery that:
- Runs at midnight (`schedule="0 0 * * *"`)
- Uses incremental resolvers for efficient processing
- Stores results both online and offline

```python
from chalk import ScheduledQuery, NamedQuery
from src.models import Transaction


# Scheduled Queries allow you to compute a specified
# set of features on a schedule, useful for persisting
# values to the online and offline stores.
# https://docs.chalk.ai/docs/scheduled-query

sq = ScheduledQuery(
    name="run_fraud_model",
    schedule="0 0 * * *",  # Every day at midnight
    output=[
        Transaction.is_fraud,
    ],
    store_online=True,
    store_offline=True,
    tags=["model_sample"],
    incremental_resolvers=["get_transactions_offline"],
)
```


## Project Structure

```
src/
├── models.py                    # Feature definitions for User and Transaction
├── queries.py                   # Scheduled query configuration
├── datasources.py               # Data source configurations
└── resolvers/
    ├── sql/
    │   ├── get_transactions_offline.chalk.sql  # Incremental transaction loading
    │   └── get_users_offline.chalk.sql         # User data loading
    └── fraud_model.py      # ONNX model wrapper and @offline resolver

models/
└── fraud_model.onnx            # Pre-trained fraud detection model

tests/
└── test_batch_prediction.py    # Unit tests for the fraud model
```

## Running the Example

1. Configure your Snowflake connection in `src/datasources.py`
2. Deploy to Chalk: `chalk apply`
3. The scheduled query will run daily, or trigger manually for testing

## Model Features

The fraud detection model uses the following features:
- Transaction amount
- Time since user's last transaction
- Number of transactions in 1d, 10d, 30d windows
- Number of distinct merchants in 1d, 10d, 30d windows
