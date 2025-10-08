-- Resolves: ProductArea
-- source: postgres
select
    name as type,
    created_at,
    description
from product_areas
