from typing import TYPE_CHECKING

from chalk.features import (
    Primary,
    features,
)

if TYPE_CHECKING:
    from src.github.features.search import GithubSearch


@features
class GithubRepoDocVDB:
    # from vector database
    path: Primary[str]
    query: "GithubSearch.query" = ""
    url: str
    distance: float | None
    ai_summary: str
    query_type: str = "VECTOR"
