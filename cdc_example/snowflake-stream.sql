-- Create target tables in Snowflake
CREATE OR REPLACE TABLE users (
    id INTEGER,
    name VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP_TZ,
    updated_at TIMESTAMP_TZ,
    _cdc_operation VARCHAR(10),
    _cdc_timestamp TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE TABLE credit_card_transactions (
    id INTEGER,
    user_id INTEGER,
    amount DECIMAL(10,2),
    merchant VARCHAR(255),
    transaction_date TIMESTAMP_TZ,
    status VARCHAR(20),
    _cdc_operation VARCHAR(10),
    _cdc_timestamp TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP
);

-- Create Snowpipe for users
CREATE OR REPLACE PIPE users_pipe
  AUTO_INGEST = TRUE
  AS
  COPY INTO users (id, name, email, created_at, updated_at, _cdc_operation)
  FROM (
    SELECT 
      PARSE_JSON($1):id::INTEGER,
      PARSE_JSON($1):name::VARCHAR,
      PARSE_JSON($1):email::VARCHAR,
      PARSE_JSON($1):created_at::TIMESTAMP_TZ,
      PARSE_JSON($1):updated_at::TIMESTAMP_TZ,
      PARSE_JSON($1):op::VARCHAR
    FROM @kafka_stage/postgres.public.users
  );

-- Create Snowpipe for transactions
CREATE OR REPLACE PIPE transactions_pipe
  AUTO_INGEST = TRUE
  AS
  COPY INTO credit_card_transactions (
    id, user_id, amount, merchant, transaction_date, status, _cdc_operation
  )
  FROM (
    SELECT 
      PARSE_JSON($1):id::INTEGER,
      PARSE_JSON($1):user_id::INTEGER,
      PARSE_JSON($1):amount::DECIMAL(10,2),
      PARSE_JSON($1):merchant::VARCHAR,
      PARSE_JSON($1):transaction_date::TIMESTAMP_TZ,
      PARSE_JSON($1):status::VARCHAR,
      PARSE_JSON($1):op::VARCHAR
    FROM @kafka_stage/postgres.public.credit_card_transactions
  );
