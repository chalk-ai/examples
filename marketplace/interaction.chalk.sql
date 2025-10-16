-- resolves: Interaction
-- source: postgres
select
    hid as id,
    created_at,
    interaction_type,
    seller_hid as seller_id,
    user_hid as user_id,
    product_hid as item_id,
    price
from marketplace_interactions
