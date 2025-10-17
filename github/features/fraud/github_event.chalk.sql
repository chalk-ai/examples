-- type: online
-- resolves: GithubEvent
-- source: postgres
select
    event_id as id,
    event_type as type,
    created_at,
    public,
    payload_action,
    repo_id,
    repo_name,
    -- actor_id as user_id,
    actor_login as username
from github_events
