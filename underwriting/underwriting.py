import logging
from datetime import datetime, timedelta

import duckdb
import polars as pl
import pytest
from chalk import DataFrame, Now, has_many, offline
from chalk.features import features
from chalk.sql._internal.integrations.duckdb import DuckDbSourceImpl
from polars.testing import assert_frame_equal

# _db = DuckDbSourceImpl(database=":memory:")
# _engine = _db.get_engine()
_db = DuckDbSourceImpl(database="foo5.duck")

_logger = logging.getLogger(__name__)


@features
class RApplication:
    id: int

    most_recent_revenue: float

    records: "DataFrame[RQuickbooksRecord]" = has_many(lambda: RApplication.id == RQuickbooksRecord.app_id)


@features
class RQuickbooksRecord:
    id: int

    app_id: int

    created_at: datetime
    start_date: datetime
    end_date: datetime

    revenue: float
    current_assets: float
    current_liabilities: float


now = datetime.now()


records_db = [
    RQuickbooksRecord(
        id=j * 100 + i,
        app_id=j,
        created_at=now - timedelta(days=i * 30),
        start_date=now - timedelta(days=i * 30),
        end_date=now - timedelta(days=i * 30),
        revenue=i,
        current_assets=i,
        current_liabilities=-i,
    )
    for i in range(12)
    for j in range(100)
]


@offline(tags="scalar-records")
def get_records_scalar(id: RApplication.id) -> DataFrame[RQuickbooksRecord]:
    return _db.query_string(
        "select * from records where app_id = :app_id",
        args={
            "app_id": id,
        },
        fields={
            "id": RQuickbooksRecord.id,
            "app_id": RQuickbooksRecord.app_id,
            "created_at": RQuickbooksRecord.created_at,
            "start_date": RQuickbooksRecord.start_date,
            "end_date": RQuickbooksRecord.end_date,
            "revenue": RQuickbooksRecord.revenue,
            "current_assets": RQuickbooksRecord.current_assets,
            "current_liabilities": RQuickbooksRecord.current_liabilities,
        },
    ).all()


@offline(tags="batch-records")
def get_records() -> DataFrame[RQuickbooksRecord]:
    return _db.query_string(
        "select * from records",
        fields={
            "id": RQuickbooksRecord.id,
            "app_id": RQuickbooksRecord.app_id,
            "created_at": RQuickbooksRecord.created_at,
            "start_date": RQuickbooksRecord.start_date,
            "end_date": RQuickbooksRecord.end_date,
            "revenue": RQuickbooksRecord.revenue,
            "current_assets": RQuickbooksRecord.current_assets,
            "current_liabilities": RQuickbooksRecord.current_liabilities,
        },
    ).all()


@offline(tags="scalar-most-recent-revenue")
def most_recent_revenue(
        records: RApplication.records[RQuickbooksRecord.revenue, RQuickbooksRecord.created_at], now: Now
) -> RApplication.most_recent_revenue:
    df: pl.LazyFrame = records.to_polars()

    x = (
        df.sort(by=str(RQuickbooksRecord.created_at), descending=True)
            .filter(pl.col(str(RQuickbooksRecord.created_at)) <= now)
            .head(1)
            .select(pl.col(str(RQuickbooksRecord.revenue)))
            .collect()
    )

    return x


@offline(tags="batch-most-recent-revenue")
def batch_most_recent_revenue(
        records: DataFrame[RApplication.id, RApplication.records, Now]
) -> DataFrame[RApplication.id, RApplication.most_recent_revenue]:
    df: pl.LazyFrame = records.to_polars()

    x = (
        df.sort(by=str(RQuickbooksRecord.created_at), descending=True)
            .filter(pl.col(str(RQuickbooksRecord.created_at)) <= now)
            .head(1)
            .select(pl.col(str(RQuickbooksRecord.revenue)))
            .collect()
    )

    return x


@pytest.fixture()
def db_fixture():
    try:
        _db.get_engine().execute("select count(*) from records")
    except:
        pa_table = DataFrame(records_db).to_pyarrow(prefixed=False)
        _db.get_engine().execute("CREATE TABLE IF NOT EXISTS records AS SELECT * FROM pa_table")


def test_simple(local_chalk_client, db_fixture):
    ds = local_chalk_client.offline_query(
        input={RQuickbooksRecord.id: [1]},
        output=[RQuickbooksRecord.revenue],
        recompute_features=True,
        tags=["batch-records", "scalar-most-recent-revenue"],
    )

    assert_frame_equal(
        ds.get_data_as_polars().collect(),
        pl.DataFrame({str(RQuickbooksRecord.id): [1], str(RQuickbooksRecord.revenue): [1.0]}),
        check_column_order=False,
    )


def test_aggregation_time_oblivious(local_chalk_client, db_fixture):
    ds = local_chalk_client.offline_query(
        input={RApplication.id: [1]},
        output=[RApplication.most_recent_revenue],
        recompute_features=True,
        tags=["batch-records", "scalar-most-recent-revenue"],
    )

    assert_frame_equal(
        ds.get_data_as_polars().collect(),
        pl.DataFrame({str(RApplication.id): [1], str(RApplication.most_recent_revenue): [0.0]}),
        check_column_order=False,
    )


def test_aggregation_time_aware(local_chalk_client, db_fixture):
    ds = local_chalk_client.offline_query(
        input={RApplication.id: [1, 1]},
        input_times=[now, now - timedelta(days=60)],
        output=[RApplication.most_recent_revenue],
        recompute_features=True,
        tags=["batch-records", "scalar-most-recent-revenue"],
    )

    assert_frame_equal(
        ds.get_data_as_polars().collect(),
        pl.DataFrame({str(RApplication.id): [1, 1], str(RApplication.most_recent_revenue): [0.0, 2.0]}),
        check_column_order=False,
    )
