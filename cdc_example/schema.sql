-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create credit_card_transactions table
CREATE TABLE credit_card_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    merchant VARCHAR(255) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    CONSTRAINT amount_positive CHECK (amount > 0)
);

-- Add sample data for users
INSERT INTO users (name, email) VALUES
    ('John Doe', 'john.doe@example.com'),
    ('Jane Smith', 'jane.smith@example.com'),
    ('Bob Wilson', 'bob.wilson@example.com'),
    ('Alice Brown', 'alice.brown@example.com'),
    ('Charlie Davis', 'charlie.davis@example.com');

-- Add sample transactions with a reasonable distribution
INSERT INTO credit_card_transactions (user_id, amount, merchant, transaction_date, status) VALUES
    (1, 25.99, 'Coffee Shop', CURRENT_TIMESTAMP - INTERVAL '2 days', 'completed'),
    (1, 85.50, 'Grocery Store', CURRENT_TIMESTAMP - INTERVAL '1 day', 'completed'),
    (2, 150.00, 'Electronics Store', CURRENT_TIMESTAMP - INTERVAL '3 days', 'completed'),
    (2, 45.75, 'Restaurant', CURRENT_TIMESTAMP - INTERVAL '12 hours', 'completed'),
    (3, 12.99, 'Streaming Service', CURRENT_TIMESTAMP - INTERVAL '5 days', 'completed'),
    (3, 250.00, 'Department Store', CURRENT_TIMESTAMP - INTERVAL '2 days', 'completed'),
    (4, 75.25, 'Gas Station', CURRENT_TIMESTAMP - INTERVAL '1 day', 'completed'),
    (4, 32.50, 'Pharmacy', CURRENT_TIMESTAMP - INTERVAL '4 hours', 'completed'),
    (5, 199.99, 'Online Shopping', CURRENT_TIMESTAMP - INTERVAL '3 days', 'completed'),
    (5, 15.00, 'Fast Food', CURRENT_TIMESTAMP - INTERVAL '6 hours', 'completed');

-- Create Debezium-compatible replica identity
ALTER TABLE users REPLICA IDENTITY FULL;
ALTER TABLE credit_card_transactions REPLICA IDENTITY FULL;
