from chalk.sql import SnowflakeSource
from chalk.streams import KafkaSource

kafka = KafkaSource(name="txns_data_stream", topic="transactions")
snowflake = SnowflakeSource(name="user_db")
