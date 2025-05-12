-- resolves: Transaction
-- source: postgres
select
    id,
    amount,
    user_id,
    at,
    description as memo
from txns
