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

from src.marketplace.models import ItemDocument, ItemSearch

if TYPE_CHECKING:
    from lancedb.table import Table

db: DBConnection | None = None

DB_URI: str = "db://marketplace-x205j4"
TABLE_NAME: str = "marketplace_product_descriptions"
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
def get_vector_search_results(
    vector: ItemSearch.vector,
    q: ItemSearch.q,
    query_type: ItemSearch.query_type,
) -> DataFrame[ItemDocument]:
    def execute_vector_search(vector, q: str) -> DataFrame[ItemDocument]:
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
                    "hid",
                    "title",
                    # "description",
                ],
            )
            .limit(
                limit=30,
            )
            .to_list()
        )
        documents: list[ItemDocument] = [
            ItemDocument(
                query=q,
                id=result["hid"],
                distance=result["_distance"],
                query_type=query_type,
                title=result["title"],
                # description=result["description"],
            )
            for result in results
        ]
        return DataFrame(documents)

    match query_type:
        case "vector":
            return execute_vector_search(vector=vector, q=q)

        case _:
            raise ValueError(f"Unsupported query_type: {query_type}")
