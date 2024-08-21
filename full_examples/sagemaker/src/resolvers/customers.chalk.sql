-- resolves: Customer
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
