import chalk.functions as F
from chalk.features import (
    Primary,
    _,
    features,
    has_one,
)

from src.github.features import (
    GithubArchive,
    GithubRepo,
    GithubRepoDocVDB,
    GithubUser,
)


@features
class GithubProject:
    path: Primary[str]
    project_is_valid_repo_path: bool = F.regexp_like(
        expr=_.path,
        pattern=r"^[a-zA-Z0-9_-]+\/[a-zA-Z0-9._-]+$",
    )
    project_url: str | None = F.if_then_else(
        condition=_.project_is_valid_repo_path,
        if_true="https://github.com/" + _.path,
        if_false=None,
    )

    username: GithubUser.name = F.split_part(
        expr=_.path,
        delimiter="/",
        index=0,
    )

    user: GithubUser | None = has_one(
        lambda: GithubProject.username == GithubUser.name,
    )

    repo: GithubRepo = has_one(
        lambda: GithubProject.path == GithubRepo.path,
    )
    repo_language: str | None = F.coalesce(
        _.repo.language,
        "MISSING",
    )

    archive: GithubArchive | None = has_one(
        lambda: GithubProject.path == GithubArchive.path,
    )
    vdb: GithubRepoDocVDB | None = has_one(
        lambda: GithubProject.path == GithubRepoDocVDB.path,
    )
