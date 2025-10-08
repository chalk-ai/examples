-- Resolves: CustomerInteraction
-- source: postgres
select
    id,
    created_at,
    sentiment_rating,
    correspondence_subject,
    correspondence_body,
    communication_channel,
    communication_direction,
    user_event_id,
    user_id,
    product_area_id
from correspondences
