-- type: online
-- resolves: GithubRepo
-- source: postgres
-- ELVIS: TODO: DISABLED USING THE ACTUAL PYTHON
select
    id,
    hid,
    node_id,
    name,
    full_name,
    html_url,
    description,
    url,
    created_at,
    updated_at,
    pushed_at,
    homepage,
    size,
    stargazers_count,
    watchers_count,
    language,
    has_issues,
    forks_count,
    archived,
    open_issues_count,
    license,
    visibility,
    forks,
    open_issues,
    watchers,
    default_branch,
    owner as owner_id
from github_repos_elvis
;
