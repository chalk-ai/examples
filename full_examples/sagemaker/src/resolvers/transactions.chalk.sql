-- resolves: Transaction
-- source: postgres
select
  id,
  amt,
  customer_id,
  confirmed_fraud,
  created_at as at
from
  transactions;
