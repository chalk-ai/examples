-- name: get_user
-- resolver: User
SELECT 
    id,
    name,
    email,
    created_at,
    updated_at
FROM users
WHERE id = :id;

-- name: get_transaction
-- resolver: Transaction
SELECT 
    id,
    user_id,
    amount,
    merchant,
    transaction_date,
    status
FROM credit_card_transactions
WHERE id = :id;

-- name: get_user_transactions
-- resolver: DataFrame[Transaction]
SELECT 
    id,
    user_id,
    amount,
    merchant,
    transaction_date,
    status
FROM credit_card_transactions
WHERE user_id = :user_id
ORDER BY transaction_date DESC;

-- name: get_all_users
-- resolver: DataFrame[User]
SELECT 
    id,
    name,
    email,
    created_at,
    updated_at
FROM users;

-- name: get_all_transactions
-- resolver: DataFrame[Transaction]
SELECT 
    id,
    user_id,
    amount,
    merchant,
    transaction_date,
    status
FROM credit_card_transactions;
