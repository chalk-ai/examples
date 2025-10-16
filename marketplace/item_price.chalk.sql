-- resolves: ItemPrice
-- source: postgres
select
    hid as id,
    price as value,
    created_at ,
    product_hid as item_id,
    seller_hid as seller_id
from marketplace_product_prices
