-- type: online
-- resolves: FathomMessage
-- source: clickhouse
select
    id,
    recording_id,
    message_id,
    url,
    title,
    date,
    timestamp,
    speaker,
    organization as organization_raw,
    message,
    action_item,
    watch_link
from "fathom-messages-etl-01"
;
