-- resolves: Seller
-- source: postgres
select
    hid as id,
    created_at,
    name,
    zipcode,
    email,
    phone_number
from marketplace_sellers
