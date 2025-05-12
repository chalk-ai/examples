-- resolves: Transaction
-- source: bigquery
-- type: offline
select
    id,
    amount,
    user_id,
    updated_at as at,
    description as memo
from transactions_log
