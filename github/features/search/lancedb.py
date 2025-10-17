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

from src.github.features.github_feature_set import GithubProject, GithubRepoDocVDB
from src.github.features.search.github_search import GithubSearch

if TYPE_CHECKING:
    from lancedb.table import Table

db: DBConnection | None = None

DB_URI: str = "uri"
TABLE_NAME: str = "github_repo_documents"
DESCRIPTION_COLUMN_NAME: str = "description"
VECTOR_COLUMN_NAME: str = "vector"
REGION: str = "us-east-1"


@before_all
def init_client() -> None:
    global db
    lance_api_key: str | None = os.getenv("LANCEDB_API_KEY")
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
def get_github_search_results(
    vector: GithubSearch.vector,
    limit: GithubSearch.limit,
    query: GithubSearch.query,
) -> GithubSearch.results:
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
                "path",
                "url",
                "description",
            ],
        )
        .limit(
            limit=limit,
        )
        .to_list()
    )
    repos: list[GithubRepoDocVDB] = [
        GithubRepoDocVDB(
            path=result["path"],
            query=query,
            url=result["url"],
            distance=result["_distance"],
            ai_summary=result["description"],
            query_type="VECTOR",
        )
        for result in results
    ]
    return DataFrame(repos)


@online
def get_github_project_document(
    path: GithubProject.path,
) -> GithubProject.vdb:
    tbl: Table = db.open_table(
        name=TABLE_NAME,
    )
    results: list = (
        tbl.search()
        .where(
            f"path = '{path}'",
            prefilter=True,
        )
        .select(
            columns=[
                "path",
                "url",
                "description",
            ],
        )
        .limit(
            limit=1,
        )
        .to_list()
    )
    missing: str = "Not found in vector database."
    if len(results) == 0:
        return GithubRepoDocVDB(
            path=path,
            query="",
            url=missing,
            ai_summary=missing,
            query_type="DIRECT",
            distance=None,
        )

    repos: list[GithubRepoDocVDB] = [
        GithubRepoDocVDB(
            path=result["path"],
            query="",
            url=result["url"],
            ai_summary=result["description"],
            query_type="DIRECT",
            distance=None,
        )
        for result in results
    ]
    return repos[0]
    # return GithubProject(
    #     vdb=repos[0],
    # )
