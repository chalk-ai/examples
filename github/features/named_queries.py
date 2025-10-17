from chalk.queries.named_query import NamedQuery

from .github_feature_set import GithubProject

NamedQuery(
    name="github_project",
    input=[GithubProject.path],
    output=[
        GithubProject.project_is_valid_repo_path,
        GithubProject.project_url,
        GithubProject.username,
        GithubProject.repo.description,  # project_description
        GithubProject.archive.stars,  # project_stars_last_year_from_gh_archive
        GithubProject.repo.stargazers_count,  # project_stars_from_api
        GithubProject.vdb.ai_summary,  # project_summary_from_vdb
        GithubProject.repo.created_at,  # repo_created_at
        GithubProject.repo.forks_count,  # repo_forks
        GithubProject.repo.homepage,  # repo_homepage_url
        GithubProject.repo.open_issues_count,  # repo_issues
        GithubProject.repo.size,  # repo_size_in_kb
        GithubProject.user.bio,  # user_bio
        GithubProject.user.email,  # user_email
        GithubProject.user.location,  # user_location
    ],
)
