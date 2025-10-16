# trunk-ignore-all(pyright/reportInvalidTypeForm,pyright/reportCallIssue,ruff/PLW0603,pyright/reportOptionalMemberAccess)
import os
from typing import TYPE_CHECKING

import lancedb
from chalk.features import (
    DataFrame,
    before_all,
    online,
)
from chalk.logging import chalk_logger
from lancedb.db import DBConnection

from src.marketplace.models import ReviewDocument, ReviewSearch

if TYPE_CHECKING:
    from lancedb.table import Table

db: DBConnection | None = None

DB_URI: str = "db://marketplace-x205j4"
TABLE_NAME: str = "marketplace_products"
VECTOR_COLUMN_NAME: str = "embedding"
REGION: str = "us-east-1"


@before_all
def init_client() -> None:
    global db
    lance_api_key: str | None = os.getenv("LANCEDB_API_KEY_MARKETPLACE")
    if lance_api_key is None:
        error_msg: str = "LANCEDB_API_KEY is not set."
        chalk_logger.error(msg=error_msg)
        raise ValueError(error_msg)

    db = lancedb.connect(
        uri=DB_URI,
        api_key=lance_api_key,
        region=REGION,
    )
    chalk_logger.info(
        msg=f"Initializing client: LanceDB",
    )


@online
def get_review_search_results(
    vector: ReviewSearch.vector,
    q: ReviewSearch.q,
    query_type: ReviewSearch.query_type,
) -> DataFrame[ReviewDocument]:
    def execute_vector_search(vector, q: str) -> DataFrame[ReviewDocument]:
        tbl: Table = db.open_table(
            name=TABLE_NAME,
        )
        results: list = (
            tbl.search(
                query=vector.to_pylist(),
                query_type="vector",
                vector_column_name=VECTOR_COLUMN_NAME,
            )
            .select(
                columns=[
                    "id",
                    "title",
                ],
            )
            .limit(
                limit=10,
            )
            .to_list()
        )
        documents: list[ReviewDocument] = [
            ReviewDocument(
                query=q,
                id=result["id"],
                distance=result["_distance"],
                query_type=query_type,
                title=result["title"],
            )
            for result in results
        ]
        return DataFrame(documents)

    match query_type:
        case "vector":
            return execute_vector_search(vector=vector, q=q)

        case _:
            raise ValueError(f"Unsupported query_type: {query_type}")
