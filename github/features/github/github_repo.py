from datetime import datetime

from chalk.features import Primary, features

from .github_user import GithubUser


@features(max_staleness="28d")
class GithubRepo:
    path: Primary[str]
    full_name: str
    id: int | None
    name: str | None
    html_url: str | None
    description: str | None
    url: str | None
    created_at: datetime | None
    updated_at: datetime | None
    pushed_at: datetime | None
    homepage: str | None
    size: int | None
    stargazers_count: int | None
    watchers_count: int | None
    language: str | None
    has_issues: bool | None
    forks_count: int | None
    archived: bool | None
    open_issues_count: int | None
    license: str | None
    visibility: str | None
    forks: int | None
    open_issues: int | None
    watchers: int | None
    default_branch: str | None

    owner_id: str | None
    owner_login: GithubUser.login
    user: GithubUser

    updated_at_chalk: datetime | None
