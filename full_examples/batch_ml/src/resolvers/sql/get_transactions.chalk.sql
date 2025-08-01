-- get transactions from postgres
-- source: pg
-- resolves: Transaction
SELECT
    transaction_id as id,
    user_id,
    merchant_id,
    amount,
    ts,
    category
FROM
    transactions
