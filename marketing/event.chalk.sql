-- Resolves: Event
-- source: postgres
select
    id,
    created_at,
    name,
    product_area_type,
    user_id,
    session_id
from events
