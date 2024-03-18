
from chalk.sql import PostgreSQLSource
from chalk.streams import KafkaSource
from features import User, Seller, Interaction

pg_database = PostgreSQLSource(name="CLOUD_DB")
pg_database.with_table(name="users", features=User)
pg_database.with_table(name="sellers", features=Seller)
pg_database.with_table(name="user_interactions", features=Interaction)
