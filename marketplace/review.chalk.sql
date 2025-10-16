-- resolves: Review
-- source: postgres
select
    hid as id,
    created_at,
    star_rating,
    review_headline,
    review_body,
    product_hid as item_id,
    user_hid as user_id,
    seller_hid as seller_id
from marketplace_reviews
