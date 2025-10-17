from chalk.queries.named_query import NamedQuery
from chalk.queries.scheduled_query import ScheduledQuery

from .fathom_feature_set import (
    FathomCall,
    FathomCallAttendee,
    FathomCompany,
)

ScheduledQuery(
    name="fathom_summary",
    schedule="45 18 * * *",
    output=[
        FathomCall.id,
        FathomCall.names,
        FathomCall.attendee_count,
        FathomCall.chalk_emails,
        FathomCall.chalk_email_count,
        FathomCall.customer_emails,
        FathomCall.customer_email_count,
        FathomCall.meeting_duration_ratio,
        FathomCall.meeting_join_url,
        FathomCall.meeting_scheduled_duration,
        FathomCall.meeting_title,
        FathomCall.recording_url,
        FathomCall.recording_duration_in_minutes,
        FathomCall.speaker_changes,
        FathomCall.speaker_change_every_x_seconds,
        FathomCall.transcript,
        FathomCall.ai_call_type,
        FathomCall.ai_reasons_for_meeting,
        FathomCall.ai_risk_flag,
        FathomCall.ai_call_summary_general,
        FathomCall.webhook_status_code,
    ],
    incremental_resolvers=["fathom_call_data"],  # optional incremental source
    recompute_features=True,
    store_online=True,
    store_offline=True,
    # lower_bound=datetime(2025, 1, 1),
    # upper_bound=datetime(2025, 8, 25),
    # max_samples=10000,
    # required_resolver_tags=["fathom"]
)


NamedQuery(
    name="fathom_call",
    input=[FathomCall.id],
    output=[
        FathomCall.id,
        FathomCall.names,
        FathomCall.attendee_count,
        FathomCall.chalk_emails,
        FathomCall.chalk_email_count,
        FathomCall.customer_emails,
        FathomCall.customer_email_count,
        FathomCall.meeting_duration_ratio,
        FathomCall.meeting_join_url,
        FathomCall.meeting_scheduled_duration,
        FathomCall.meeting_title,
        FathomCall.recording_url,
        FathomCall.recording_duration_in_minutes,
        FathomCall.speaker_changes,
        FathomCall.speaker_change_every_x_seconds,
        FathomCall.transcript,
        FathomCall.ai_call_type,
        FathomCall.ai_reasons_for_meeting,
        FathomCall.ai_risk_flag,
    ],
)

NamedQuery(
    name="fathom_attendee",
    input=[FathomCallAttendee.email],
    output=[
        FathomCallAttendee.email,
        FathomCallAttendee.name,
        FathomCallAttendee.is_external,
        FathomCallAttendee.calls,
        FathomCallAttendee.all_companies_met_with,
        FathomCallAttendee.companies_met_with_count,
        FathomCallAttendee.average_recording_time,
        FathomCallAttendee.longest_recording_time,
    ],
)

NamedQuery(
    name="fathom_company",
    input=[FathomCompany.domain],
    output=[
        FathomCompany.domain,
        FathomCompany.total_call_list,
        FathomCompany.calls,
        FathomCompany.average_recording_time,
        FathomCompany.longest_recording_time,
        FathomCompany.first_meeting,
        FathomCompany.most_recent_meeting,
        FathomCompany.emails_from_domain,
        FathomCompany.employee_count,
        FathomCompany.total_recording_time,
    ],
)
