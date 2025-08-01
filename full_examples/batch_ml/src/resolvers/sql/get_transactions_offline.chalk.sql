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
