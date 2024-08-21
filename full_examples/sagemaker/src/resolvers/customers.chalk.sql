-- resolves: customer
-- source: postgres
select
  id,
  name,
  email,
  dob,
  age,
  income
from
  users;
