-- type: online
-- resolves: GithubOwner
-- source: postgres
-- ELVIS: TODO: DISABLED USING THE ACTUAL PYTHON
select
    id,
    hid,
    login,
    node_id,
    avatar_url,
    url,
    html_url,
    followers_url,
    following_url,
    starred_url,
    organizations_url,
    repos_url,
    type
from github_owner
