# CDC Example: PostgreSQL → Kafka → Snowflake with Chalk Features

This example demonstrates Change Data Capture (CDC) from PostgreSQL to Snowflake via Kafka, with Chalk feature definitions.

## Components

1. **PostgreSQL Database**
   - Two tables: `users` and `credit_card_transactions`
   - Configured with logical replication for CDC
   - Sample data included

2. **Debezium CDC Connector**
   - Captures changes from PostgreSQL WAL
   - Streams changes to Kafka topics
   - Configured for both tables with JSON output

3. **Apache Kafka**
   - Acts as the message broker for CDC events
   - Topics created automatically by Debezium
   - Includes Kafka Connect for managing connectors

4. **Snowflake Integration**
   - Target tables matching source schema
   - Snowpipes for continuous data ingestion
   - CDC operation tracking

5. **Chalk Features**
   - Python classes matching database schema
   - SQL resolvers for data access
   - Relationship definitions between users and transactions

## Setup Instructions

1. Start the infrastructure:
   ```bash
   docker-compose up -d
   ```

2. Wait for all services to be healthy, then create the Debezium connector:
   ```bash
   curl -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d @debezium-connector.json
   ```

3. Configure Snowflake:
   - Create a storage integration for Kafka
   - Execute the SQL in `snowflake-stream.sql`
   - Configure authentication and network access

4. Monitor data flow:
   - Kafka UI: http://localhost:8080
   - Kafka Connect: http://localhost:8083
   - PostgreSQL: localhost:5432

## Data Model

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Transactions Table
```sql
CREATE TABLE credit_card_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    merchant VARCHAR(255) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20)
);
```

## Using Chalk Features

The Python feature definitions in `features.py` provide a type-safe way to access this data:

```python
from cdc_example.features import User, Transaction

# Get a user and their transactions
user = User.get(id=1)
transactions = user.transactions.all()
```

SQL resolvers in `resolvers.chalk.sql` provide the underlying data access layer.

## Testing Changes

1. Insert new data into PostgreSQL:
   ```sql
   INSERT INTO users (name, email) 
   VALUES ('New User', 'new.user@example.com');
   ```

2. Watch the change flow through:
   - Check Kafka UI for new messages
   - Verify data appears in Snowflake

## Monitoring

- View CDC events: Check Kafka topics `postgres.public.users` and `postgres.public.credit_card_transactions`
- Monitor Snowpipe: Check copy history and loading status in Snowflake
- Debezium status: Check connector status via Kafka Connect REST API
