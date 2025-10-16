-- resolves: User
-- source: postgres
select
    hid as id,
    created_at,
    first_name,
    last_name,
    email,
    birthday
from marketplace_users
