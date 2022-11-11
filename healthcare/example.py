from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float

from chalk import offline, online
from chalk.features import Features, sink
from chalk.sql import PostgreSQLSource
from chalk.streams import stream, KafkaSource
from chalk.streams.KafkaSource import KafkaConsumerConfig
from healthcare.helpers import StitchAPIClient, Base

# --------------------------------------
# ----- PART 1: INGESTING RAW DATA -----
# --------------------------------------

# Production Postgres CDC
curebase_postgres = PostgreSQLSource()


class CurebaseCustomerTrialSQL(Base):
    __tablename__ = "trial"

    id = Column(Integer, primary_key=True)
    trial_data = Column(String)


@offline(cron=True)
def ingest_curebase_app_data() -> DataFrame[TrialFeatures.raw_json, TrialFeatures.id]:
    return curebase_postgres.query(
        TrialFeatures(
            raw_json=CurebaseCustomerTrialSQL.trial_data,
            id=CurebaseCustomerTrialSQL.id,
        )
    ).all(incremental=True)


# Stitch
stitch_client = StitchAPIClient()


@offline(cron="10m")
def ingest_stitch_data() -> Features[AnalyticsFeatures]:
    data = stitch_client.pull_data()
    return AnalyticsFeatures(id=data.id, user_id=data.user_id, page_name=data.page_name)


# Kinesis
class SentrySQSMessage(BaseModel):
    id: str
    exception_message: str


stream_source = KafkaSource(
    message=SentrySQSMessage,
    consumer_config=KafkaConsumerConfig(broker="kafka.website.com:9092", topic="sentry_updates"),
)


@stream
def ingest_kinesis(message: SentrySQSMessage) -> Features[SentryFeatures]:
    return SentryFeatures(id=message.id, exception=message.exception_message)


# -----------------------------------------
# ----- PART 2: TRANSFORMING RAW DATA -----
# -----------------------------------------
@online
def get_trial_members(raw: TrialFeatures.raw_json) -> DataFrame[TrialMemberFeatures]:
    return DataFrame.from_list(
        TrialMemberFeatures(
            id=member["id"],
            age=member["age"],
            trial_id=raw["id"],
            is_control=raw["control"],
        )
        for member in raw["trial_details"]["members"]
    )


@online
def get_trial_name(raw: TrialFeatures.raw_json) -> TrialFeatures.trial_name:
    return raw["train_meta"]["trial_name"]


@online(cron="1m")
def get_employees() -> DataFrame[EmployeeFeatures]:
    return DataFrame.read_csv(
        "s3://wow.csv",
        columns={
            0: EmployeeFeatures.id,
            1: EmployeeFeatures.salary,
            4: EmployeeFeatures.full_name,
        },
    )


# Derived features -- super-fast iteration
@online
def get_trial_average_age(
    members: TrialFeatures.trial_member[TrialMemberFeatures.is_control is True],
) -> TrialFeatures.control_mean_age:
    return members[TrialMemberFeatures.age].mean()


# -------------------------------------
# ----- PART 3: SINKING TO LOOKER -----
# -------------------------------------

# Sinking the data to a Looker-compatible store
class LookerViewSQL(Base):
    __tablename__ = "bank_account"

    id = Column(Integer, primary_key=True)
    trial_average_age = Column(Float)


@sink(upsert=True)
def update_looker_tables(
    control_mean_age: TrialFeatures.control_mean_age,
    id: TrialFeatures.id,
) -> LookerViewSQL:
    return LookerViewSQL(id=id, trial_average_age=control_mean_age)


class LookerMemberViewSQL(Base):
    __tablename__ = "member_view"

    id = Column(Integer, primary_key=True)
    is_control = Column(Boolean)


@sink(upsert=True)
def update_looker_tables(
    age: TrialMemberFeatures.age,
    id: TrialMemberFeatures.id,
    is_control: TrialMemberFeatures.is_control,
) -> LookerViewSQL:
    return LookerMemberViewSQL(id=id, is_control=is_control)
