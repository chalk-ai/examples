import math

import requests
from chalk.features import online

from src.fathom.features.fathom_feature_set import FathomCall


@online
def get_call_chalk_emails(
    default_domain: FathomCall.chalk_domain,
    all_emails: FathomCall.all_email_addresses,
) -> FathomCall.chalk_emails:
    chalk_emails = [
        email
        for email in all_emails
        if email.split("@")[-1].lower() == default_domain.lower()
    ]
    return chalk_emails


@online
def get_call_customer_emails(
    default_domain: FathomCall.chalk_domain,
    all_emails: FathomCall.all_email_addresses,
) -> FathomCall.customer_emails:
    customer_emails = [
        email
        for email in all_emails
        if email.split("@")[-1].lower() != default_domain.lower()
    ]
    return customer_emails


@online
def get_call_customer_domains(
    default_domain: FathomCall.chalk_domain,
    all_emails: FathomCall.all_email_addresses,
) -> FathomCall.customer_domains:
    customer_domains = {
        email.split("@")[-1].lower()  # Extract the domain from each email
        for email in all_emails
        if email.split("@")[-1].lower() != default_domain.lower()
    }
    return list(customer_domains)  # Convert the set to a list before returning


@online
def fathom_call_webhook(
    id: FathomCall.id,
    names: FathomCall.names,
    all_email_addresses: FathomCall.all_email_addresses,
    attendee_count: FathomCall.attendee_count,
    chalk_emails: FathomCall.chalk_emails,
    chalk_email_count: FathomCall.chalk_email_count,
    customer_emails: FathomCall.customer_emails,
    customer_email_count: FathomCall.customer_email_count,
    customer_domains: FathomCall.customer_domains,
    recording_url: FathomCall.recording_url,
    meeting_join_url: FathomCall.meeting_join_url,
    meeting_title: FathomCall.meeting_title,
    meeting_scheduled_start_time: FathomCall.meeting_scheduled_start_time,
    meeting_scheduled_end_time: FathomCall.meeting_scheduled_end_time,
    meeting_scheduled_duration: FathomCall.meeting_scheduled_duration,
    recording_duration_in_minutes: FathomCall.recording_duration_in_minutes,
    speaker_changes: FathomCall.speaker_changes,
    speaker_change_every_x_seconds: FathomCall.speaker_change_every_x_seconds,
    meeting_duration_ratio: FathomCall.meeting_duration_ratio,
    ai_call_summary_general: FathomCall.ai_call_summary_general,
    # ai_call_summary_sales: FathomCall.ai_call_summary_sales,
    # ai_call_summary_marketing: FathomCall.ai_call_summary_marketing, # TOOD(dani): revive once we've finished prompt engineering
    ai_call_type: FathomCall.ai_call_type,
    ai_reasons_for_meeting: FathomCall.ai_reasons_for_meeting,
    ai_risk_flag: FathomCall.ai_risk_flag,
) -> FathomCall.webhook_status_code:
    customer_domains_joined: str
    if len(customer_domains) == 0:
        customer_domains_joined = "Chalk"

    elif len(customer_domains) == 1:
        customer_domains_joined = customer_domains[0]

    else:
        customer_domains_joined = "+".join(customer_domains)

    data = {
        "id": id,
        "names": names,
        "meeting_title": meeting_title,
        "meeting_join_url": meeting_join_url,
        "recording_url": recording_url,
        "meeting_scheduled_start_time": str(meeting_scheduled_start_time),
        "meeting_scheduled_end_time": str(meeting_scheduled_end_time),
        "meeting_scheduled_duration": (
            meeting_scheduled_duration
            if meeting_scheduled_duration is not None
            and not (
                math.isnan(meeting_scheduled_duration)
                or math.isinf(meeting_scheduled_duration)
            )
            else None
        ),
        "meeting_duration_ratio": (
            meeting_duration_ratio
            if meeting_duration_ratio is not None
            and not (
                math.isnan(meeting_duration_ratio) or math.isinf(meeting_duration_ratio)
            )
            else None
        ),
        # Recording details
        "recording_duration_in_minutes": (
            recording_duration_in_minutes
            if recording_duration_in_minutes is not None
            and not (
                math.isnan(recording_duration_in_minutes)
                or math.isinf(recording_duration_in_minutes)
            )
            else 0
        ),
        # Participants
        "all_email_addresses": all_email_addresses,
        "attendee_count": attendee_count if attendee_count else 0,
        "chalk_emails": chalk_emails,
        "chalk_email_count": chalk_email_count if chalk_email_count else 0,
        "customer_emails": customer_emails,
        "customer_email_count": customer_email_count if customer_email_count else 0,
        "customer_domains": customer_domains,
        "customer_domains_joined": customer_domains_joined,
        # AI-related summaries
        "ai_call_summary_general": (
            ai_call_summary_general
            if ai_call_summary_general is not None and ai_call_summary_general.strip()
            else "N/A"
        ),
        # "ai_call_summary_sales": (
        #     ai_call_summary_sales
        #     if ai_call_summary_sales is not None and ai_call_summary_sales.strip()
        #     else "N/A"
        # ),
        # "ai_call_summary_marketing": ( # TODO(dani): revive once we've finished prompt engineering
        #     ai_call_summary_marketing
        #     if ai_call_summary_marketing is not None
        #     and ai_call_summary_marketing.strip()
        #     else "N/A"
        # ),
        "ai_call_type": (
            ai_call_type if ai_call_type is not None and ai_call_type.strip() else "N/A"
        ),
        "ai_reasons_for_meeting": (
            ai_reasons_for_meeting
            if ai_reasons_for_meeting is not None and ai_reasons_for_meeting.strip()
            else "N/A"
        ),
        "ai_risk_flags": (
            ai_risk_flag if ai_risk_flag is not None and ai_risk_flag.strip() else "N/A"
        ),
        # Speaker details
        "speaker_changes": (
            speaker_changes
            if speaker_changes is not None
            and not (math.isnan(speaker_changes) or math.isinf(speaker_changes))
            else None
        ),
        "speaker_change_every_x_seconds": (
            speaker_change_every_x_seconds
            if speaker_change_every_x_seconds is not None
            and not (
                math.isnan(speaker_change_every_x_seconds)
                or math.isinf(speaker_change_every_x_seconds)
            )
            else None
        ),
    }
    status_code = requests.post(
        headers={"Content-Type": "application/json"},
        url="https://hkdk.events/vtqjv0f6wmlm7z",
        json=data,
    ).status_code
    return status_code
