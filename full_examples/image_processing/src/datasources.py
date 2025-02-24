from chalk.sql import PostgreSQLSource
from chalk.streams import KafkaSource

postgres = PostgreSQLSource(name="pg")
kafka_stream = KafkaSource(name="stream")
