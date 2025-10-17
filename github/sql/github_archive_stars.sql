-- type: online
-- resolves: GithubArchive
-- source: postgres
select id, name as path, url as api_url, stars
from github_archive_stars
order by stars desc
limit 100
;
