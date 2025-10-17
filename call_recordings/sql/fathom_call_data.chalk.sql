-- type: online
-- resolves: FathomCallData
-- source: clickhouse
-- incremental:
--   mode: row
--   incremental_column: meeting_scheduled_start_time
select
    id,
    recording_id as call_id,

    CAST(meeting_scheduled_start_time AS DATETIME) as meeting_scheduled_start_time,
    CASE
        WHEN meeting_scheduled_end_time IS NOT NULL
        THEN CAST(meeting_scheduled_end_time AS DATETIME)
        ELSE NULL
    END as meeting_scheduled_end_time,

    meeting_has_external_invitees as has_external_attandees,

    meeting_invitees_name as attendee_name,
    meeting_invitees_email as attendee_email,
    meeting_invitees_is_external as attendee_is_external,
    meeting_external_domains_domain_name as company_domain,

    meeting_join_url,
    meeting_scheduled_duration_in_minutes,
    meeting_title,
    recording_duration_in_minutes,
    recording_url,
    transcript_plaintext
from "fathom-calls-etl"
;
