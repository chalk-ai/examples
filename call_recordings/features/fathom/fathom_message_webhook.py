import requests
from chalk.features import online

from src.fathom.features.fathom_feature_set import FathomMessage


@online
def fathom_message_webhook(
    id: FathomMessage.id,
    recording_id: FathomMessage.recording_id,
    message_id: FathomMessage.message_id,
    url: FathomMessage.url,
    title: FathomMessage.title,
    date: FathomMessage.date,
    timestamp: FathomMessage.timestamp,
    speaker: FathomMessage.speaker,
    organization: FathomMessage.organization,
    message: FathomMessage.message,
    action_item: FathomMessage.action_item,
    watch_link: FathomMessage.watch_link,
    speaker_changes: FathomMessage.call.speaker_changes,
    meeting_duration_ratio: FathomMessage.call.meeting_duration_ratio,
    attendee_count: FathomMessage.call.attendee_count,
    chalk_attendee_count: FathomMessage.call.chalk_email_count,
    customer_attendee_count: FathomMessage.call.customer_email_count,
    meeting_scheduled_duration: FathomMessage.call.meeting_scheduled_duration,
    recording_duration_in_minutes: FathomMessage.call.recording_duration_in_minutes,
    ai_meeting_type: FathomMessage.call.ai_call_type,
    ai_reasons_for_meeting: FathomMessage.call.ai_reasons_for_meeting,
    ai_risk_flags: FathomMessage.call.ai_risk_flag,
) -> FathomMessage.webhook_status_code:
    data = {
        "id": id,
        "url": url,
        "date": date.isoformat(),
        "title": title,
        "message": message,
        "speaker": speaker,
        "timestamp": timestamp,
        "message_id": message_id,
        "watch_link": watch_link,
        "action_item": action_item,
        "organization": organization,
        "recording_id": recording_id,
        "attendee_count": attendee_count,
        "chalk_attendee_count": chalk_attendee_count,
        "customer_attendee_count": customer_attendee_count,
        "meeting_scheduled_duration": meeting_scheduled_duration,
        "recording_duration_in_minutes": recording_duration_in_minutes,
        "speaker_changes": speaker_changes,
        "meeting_duration_ratio": meeting_duration_ratio,
        "ai_meeting_type": ai_meeting_type,
        "ai_reasons_for_meeting": ai_reasons_for_meeting,
        "ai_risk_flags": ai_risk_flags,
    }
    status_code = requests.post(
        headers={"Content-Type": "application/json"},
        url="url",
        json=data,
    ).status_code
    if status_code == 200:
        return 200

    return None
