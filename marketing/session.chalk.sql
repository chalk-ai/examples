-- Resolves: Session
-- source: postgres
select
    id,
    created_at,
    end_at,
    duration,
    user_id
from sessions
