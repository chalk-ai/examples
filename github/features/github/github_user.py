from datetime import datetime

import chalk.functions as F
from chalk.features import DataFrame, Primary, _, features, has_many


@features
class GithubUserStarredRepo:
    path: Primary[str]
    description: str | None
    homepage: str | None
    stargazers_count: int | None
    language: str | None
    license: str | None
    open_issues_count: int | None
    forks_count: int | None
    url_html: str | None
    url_api: str | None

    username: str


def parse_starred_github_repos_for_github_user(
    username: str,
    repo_data: dict | None,
) -> GithubUserStarredRepo | None:
    if repo_data is None or not repo_data:
        return None

    repo_license: str = "MISSING"
    if temp_license_data := repo_data.get("license"):
        if temp_license := temp_license_data.get("spdx_id"):
            repo_license = str(temp_license)

    path: str | None = repo_data.get("full_name")
    return GithubUserStarredRepo(
        username=username,
        path=path,
        description=repo_data.get("description"),
        homepage=repo_data.get("homepage"),
        stargazers_count=repo_data.get("stargazers_count"),
        language=repo_data.get("language"),
        license=repo_license,
        open_issues_count=repo_data.get("open_issues_count"),
        forks_count=repo_data.get("forks_count"),
        url_api=repo_data.get("url"),
        url_html=repo_data.get("html_url"),
    )


@features(max_staleness="infinity")
class GithubUser:
    login: str
    name: Primary[str]
    id: int
    node_id: str
    bio: str | None
    blog: str
    company: str | None
    created_at: datetime | None
    email: str | None
    events_url: str | None
    followers: int
    following: int
    full_name: str | None
    gists_url: str | None
    gravatar_id: str | None
    hireable: bool | None
    location: str | None
    public_gists: int
    public_repos: int
    received_events_url: str | None
    site_admin: bool | None
    subscriptions_url: str | None
    twitter_username: str | None
    updated_at: datetime | None
    user_view_type: str | None
    url_api: str
    url_avatar: str
    url_html: str
    url_followers: str
    url_following: str
    url_starred: str
    url_organizations: str
    url_repos: str
    type: str

    updated_at_chalk: datetime

    starred_repos: DataFrame[GithubUserStarredRepo] = has_many(
        lambda: GithubUser.name == GithubUserStarredRepo.username,
    )
    starred_most_recent_path: str = F.array_join(
        F.head(
            _.starred_repos[_.path],
            n=1,
        ),
        delimiter="",
    )
    starred_most_recent_url: str | None = (
        "https://github.com/" + _.starred_most_recent_path
    )
