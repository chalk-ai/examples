-- get transactions from postgres
-- source: pg
-- resolves: User
SELECT
    transaction_id as id,
    user_id,
    merchant_id,
    amount,
    ts
FROM
    transactions
