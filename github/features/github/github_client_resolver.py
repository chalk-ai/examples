# trunk-ignore-all(pyright/reportInvalidTypeForm,pyright/reportCallIssue,pyright/reportOptionalMemberAccess)
import os
from typing import TYPE_CHECKING

import httpx
import orjson
from chalk.features import DataFrame, Features, before_all, online
from chalk.features.pseudofeatures import Now
from chalk.logging import chalk_logger

from github import Auth, Github

from .github_repo import GithubRepo
from .github_user import (
    GithubUser,
    GithubUserStarredRepo,
    parse_starred_github_repos_for_github_user,
)

if TYPE_CHECKING:
    from github.NamedUser import NamedUser
    from github.Repository import Repository

client: Github | None = None


@before_all
def init_client() -> None:
    global client  # trunk-ignore(ruff/PLW0603)
    chalk_logger.debug(
        msg="Setting up client",
    )

    github_token: str | None = os.getenv(
        "GITHUB_TOKEN",
        None,
    )
    if github_token is None:
        raise AttributeError

    client = Github(
        auth=Auth.Token(
            token=github_token,
        ),
    )


@online
def get_github_repo(
    path: GithubRepo.path,
    now: Now,
) -> Features[
    GithubRepo.name,
    GithubRepo.full_name,
    GithubRepo.html_url,
    GithubRepo.description,
    GithubRepo.url,
    GithubRepo.homepage,
    GithubRepo.language,
    GithubRepo.license,
    GithubRepo.visibility,
    GithubRepo.default_branch,
    GithubRepo.id,
    GithubRepo.size,
    GithubRepo.stargazers_count,
    GithubRepo.watchers_count,
    GithubRepo.forks_count,
    GithubRepo.open_issues_count,
    GithubRepo.forks,
    GithubRepo.open_issues,
    GithubRepo.watchers,
    GithubRepo.has_issues,
    GithubRepo.archived,
    GithubRepo.created_at,
    GithubRepo.updated_at,
    GithubRepo.pushed_at,
    GithubRepo.owner_id,
    GithubRepo.owner_login,
    GithubRepo.updated_at_chalk,
]:
    repo: Repository = client.get_repo(
        full_name_or_id=path,
    )
    repo_license: str = str(repo.license.name)
    return GithubRepo(
        full_name=path,
        name=repo.name,
        html_url=repo.html_url,
        description=repo.description,
        url=repo.url,
        homepage=repo.homepage,
        language=repo.language,
        license=repo_license,
        visibility=repo.visibility,
        default_branch=repo.default_branch,
        id=repo.id,
        size=repo.size,
        stargazers_count=repo.stargazers_count,
        watchers_count=repo.watchers_count,
        forks_count=repo.forks_count,
        open_issues_count=repo.open_issues_count,
        forks=repo.forks,
        open_issues=repo.open_issues,
        watchers=repo.watchers,
        has_issues=repo.has_issues,
        archived=repo.archived,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
        pushed_at=repo.pushed_at,
        owner_id=repo.owner.id,
        owner_login=repo.owner.login,
        updated_at_chalk=now,
    )


@online
def get_github_user(
    name: GithubUser.name,
    now: Now,
) -> Features[
    GithubUser.login,
    GithubUser.id,
    GithubUser.node_id,
    GithubUser.url_avatar,
    GithubUser.url_api,
    GithubUser.url_html,
    GithubUser.url_followers,
    GithubUser.url_following,
    GithubUser.url_starred,
    GithubUser.url_organizations,
    GithubUser.url_repos,
    GithubUser.type,
    GithubUser.updated_at_chalk,
    GithubUser.bio,
    GithubUser.blog,
    GithubUser.company,
    GithubUser.created_at,
    GithubUser.email,
    GithubUser.events_url,
    GithubUser.followers,
    GithubUser.following,
    GithubUser.gists_url,
    GithubUser.gravatar_id,
    GithubUser.hireable,
    GithubUser.location,
    GithubUser.public_gists,
    GithubUser.public_repos,
    GithubUser.received_events_url,
    GithubUser.site_admin,
    GithubUser.subscriptions_url,
    GithubUser.twitter_username,
    GithubUser.updated_at,
    GithubUser.user_view_type,
    GithubUser.full_name,
]:
    user: NamedUser = client.get_user(
        login=name,
    )
    if user.login != name:
        raise AssertionError

    def strip_placeholders(url: str) -> str:
        return url.split("{")[0]

    return GithubUser(
        login=name,
        id=user.id,
        node_id=user.node_id,
        url_avatar=user.avatar_url,
        url_api=user.url,
        url_html=user.html_url,
        url_followers=user.followers_url,
        url_following=strip_placeholders(user.following_url),
        url_starred=strip_placeholders(user.starred_url),
        url_organizations=user.organizations_url,
        url_repos=user.repos_url,
        type=user.type,
        updated_at_chalk=now,
        bio=user.bio,
        blog=user.blog,
        company=user.company,
        created_at=user.created_at,
        email=user.email,
        events_url=strip_placeholders(user.events_url),
        followers=user.followers,
        following=user.following,
        gists_url=strip_placeholders(user.gists_url),
        gravatar_id=user.gravatar_id,
        hireable=user.hireable,
        location=user.location,
        public_gists=user.public_gists,
        public_repos=user.public_repos,
        received_events_url=strip_placeholders(user.received_events_url),
        site_admin=user.site_admin,
        subscriptions_url=user.subscriptions_url,
        twitter_username=user.twitter_username,
        updated_at=user.updated_at,
        user_view_type=user.user_view_type,
        full_name=user.name,
    )


@online
def get_github_user_starred_repos(
    username: GithubUser.name,
    starred_url: GithubUser.url_starred,
) -> GithubUser.starred_repos:
    starred_repos_json: str = httpx.get(url=starred_url).text
    list_of_repos: list[dict] = orjson.loads(starred_repos_json)
    if len(list_of_repos) == 0:
        return None

    starred_repos: list[GithubUserStarredRepo] = [
        parsed_repo
        for repo_data in list_of_repos
        if (
            parsed_repo := parse_starred_github_repos_for_github_user(
                repo_data=repo_data,
                username=username,
            )
        )
        is not None
    ]
    return DataFrame(
        starred_repos,
    )
