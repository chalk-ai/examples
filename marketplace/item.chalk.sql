-- resolves: Item
-- source: postgres
select
    hid as id,
    title,
    description
from marketplace_products
