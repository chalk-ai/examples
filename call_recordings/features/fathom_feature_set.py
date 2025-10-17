# trunk-ignore-all(pyright/reportUnknownLambdaType)
from datetime import datetime

import chalk.functions as F
import chalk.prompts as P
from chalk import has_many
from chalk.features import (
    DataFrame,
    FeatureTime,
    Primary,
    _,
    feature,
    features,
    has_one,
    online,
)
from chalk.streams import Windowed, windowed

from src.fathom.features.fathom.fathom_meeting_insights_sales import (
    StructuredOutputCallInsights,
    prompt_meeting_insights_sales_user,
)
from src.fathom.features.fathom.fathom_meeting_type import (
    StructuredOutputMeetingType,
    prompt_meeting_type_user,
)

EMAIL_REGEXP: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


@features
class FathomCallData:
    id: Primary[str]
    call_id: "FathomCall.id"

    meeting_scheduled_start_time: FeatureTime
    meeting_scheduled_end_time: datetime | None

    company_domain: str | None
    has_external_attandees: bool | None

    attendee_email: str | None
    attendee_name: str | None
    attendee_is_external: bool | None

    meeting_join_url: str | None
    meeting_scheduled_duration_in_minutes: int | None
    meeting_title: str | None
    recording_duration_in_minutes: float | None
    recording_url: str | None
    transcript_plaintext: str | None


@features
class FathomCallAttendee:
    email: Primary[str]
    call_data: DataFrame[FathomCallData] = has_many(
        lambda: FathomCallAttendee.email == FathomCallData.attendee_email,
    )

    company_domain: str = F.split_part(
        expr=_.email,
        delimiter="@",
        index=1,
    )

    names: list[str] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.attendee_name]),
    )
    names_count: int = F.cardinality(arr=_.names)
    name: str | None = (
        F.when(_.names_count == 1)
        .then(
            F.element_at(
                arr=_.names,
                index=0,
            ),
        )
        .when(_.names_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )

    is_external_list: list[bool] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.attendee_is_external]),
    )
    is_external_count: int = F.cardinality(arr=_.is_external_list)
    is_external: str | None = (
        F.when(_.is_external_count == 1)
        .then(
            F.when(
                F.element_at(
                    arr=_.is_external_list,
                    index=0,
                ),
            )
            .then("true")
            .otherwise("false"),
        )
        .when(_.is_external_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )

    total_call_list: list[str] = F.array_distinct(
        arr=F.array_agg(
            expr=_.call_data[_.call_id],
        ),
    )
    calls: Windowed[int] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=F.cardinality(
            arr=F.array_distinct(
                arr=F.array_agg(
                    expr=_.call_data[
                        _.call_id,
                        _.meeting_scheduled_start_time > _.chalk_window,
                    ],
                ),
            ),
        ),
    )

    all_companies_met_with: list[str] = F.array_remove(  # removing self
        array=F.array_distinct(
            arr=F.array_agg(
                expr=_.call_data[_.company_domain],
            ),
        ),
        element=_.company_domain,
    )
    companies_met_with_count: Windowed[int] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=F.cardinality(
            arr=F.array_remove(  # removing self
                array=F.array_distinct(
                    arr=F.array_agg(
                        expr=_.call_data[
                            _.company_domain,
                            _.meeting_scheduled_start_time > _.chalk_window,
                        ],
                    ),
                ),
                element=_.company_domain,
            ),
        ),
    )

    average_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].mean(),
    )
    longest_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].max(),
    )
    total_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].sum(),
    )


@features
class FathomCompany:
    domain: Primary[str]
    call_data: DataFrame[FathomCallData] = has_many(
        lambda: FathomCompany.domain == FathomCallData.company_domain,
    )

    total_call_list: list[str] = F.array_distinct(
        arr=F.array_agg(
            expr=_.call_data[_.call_id],
        ),
    )
    calls: Windowed[int] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=F.cardinality(
            arr=F.array_distinct(
                arr=F.array_agg(
                    expr=_.call_data[
                        _.call_id,
                        _.meeting_scheduled_start_time > _.chalk_window,
                    ],
                ),
            ),
        ),
    )

    average_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].mean(),
    )
    longest_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].max(),
    )
    total_recording_time: Windowed[float] = windowed(
        "7d",
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.call_data[
            _.recording_duration_in_minutes,
            _.meeting_scheduled_start_time > _.chalk_window,
        ].sum(),
    )

    first_meeting: datetime = F.min_by(
        _.call_data[_.meeting_scheduled_start_time],
        sort=_.meeting_scheduled_start_time,
    )
    most_recent_meeting: datetime = F.max_by(
        _.call_data[_.meeting_scheduled_start_time],
        sort=_.meeting_scheduled_start_time,
    )

    all_email_addresses: list[str] = F.array_distinct(
        arr=F.remove_nulls(
            array=F.array_agg(
                expr=_.call_data[_.attendee_email],
            ),
        ),
    )
    emails_from_domain: list[str]
    employee_count: int = F.cardinality(arr=_.emails_from_domain)


@online
def get_company_emails(
    domain: FathomCompany.domain,
    all_emails: FathomCompany.all_email_addresses,
) -> FathomCompany.emails_from_domain:
    return [
        email for email in all_emails if email.split("@")[-1].lower() == domain.lower()
    ]


@features
class FathomMessage:
    id: Primary[str]
    recording_id: str
    message_id: int
    url: str
    title: str
    date: datetime
    timestamp: int
    speaker: str
    message: str
    action_item: str | None
    watch_link: str | None

    call: "FathomCall" = has_one(lambda: FathomMessage.recording_id == FathomCall.id)

    webhook_status_code: int | None

    organization_raw: str | None
    organization_etl: str | None = feature(
        max_staleness="infinity",
    )
    organization: str = F.coalesce(
        _.organization_raw,
        _.organization_etl,
        "unknown",
    )


@features
class FathomCall:
    id: Primary[str]

    chalk_domain: str = "chalk.ai"

    messages: DataFrame[FathomMessage]
    speaker_changes: int = _.messages.count()
    speaker_change_every_x_seconds: float = (
        _.recording_duration_in_minutes * 60 / _.speaker_changes
    )
    meeting_duration_ratio: float | None = (
        F.when(F.is_null(_.recording_duration_in_minutes))
        .then(None)
        .otherwise(_.recording_duration_in_minutes / _.meeting_scheduled_duration)
    )
    call_data: DataFrame[FathomCallData]

    names: list[str] = F.array_distinct(
        arr=F.array_agg(
            expr=_.call_data[_.attendee_name],
        ),
    )

    all_email_addresses: list[str] = F.array_distinct(
        arr=F.remove_nulls(
            array=F.array_agg(
                expr=_.call_data[_.attendee_email],
            ),
        ),
    )
    attendee_count: int = F.cardinality(
        arr=F.array_distinct(
            arr=F.remove_nulls(
                array=F.array_agg(
                    expr=_.call_data[_.attendee_email],
                ),
            ),
        ),
    )

    chalk_emails: list[str]
    chalk_email_count: int = F.cardinality(arr=_.chalk_emails)

    customer_emails: list[str]
    customer_email_count: int = F.cardinality(arr=_.customer_emails)

    customer_domains: list[str]
    customer_domain_count: int = F.cardinality(arr=_.customer_domains)

    meeting_title_list: list[str] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.meeting_title]),
    )
    meeting_title_count: int = F.cardinality(arr=_.meeting_title_list)
    meeting_title: str | None = (
        F.when(_.meeting_title_count == 1)
        .then(
            F.element_at(
                arr=_.meeting_title_list,
                index=0,
            ),
        )
        .when(_.meeting_title_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )

    meeting_join_url_list: list[str] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.meeting_join_url]),
    )
    meeting_join_url_count: int = F.cardinality(arr=_.meeting_join_url_list)
    meeting_join_url: str | None = (
        F.when(_.meeting_join_url_count == 1)
        .then(
            F.element_at(
                arr=_.meeting_join_url_list,
                index=0,
            ),
        )
        .when(_.meeting_join_url_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )

    meeting_scheduled_start_time_list: list[datetime] = F.array_distinct(
        arr=F.array_agg(_.call_data[_.meeting_scheduled_start_time]),
    )
    meeting_scheduled_start_time_count: int = F.cardinality(
        arr=_.meeting_scheduled_start_time_list,
    )
    meeting_scheduled_start_time: datetime | None = (
        F.when(_.meeting_scheduled_start_time_count == 1)
        .then(
            F.element_at(
                arr=_.meeting_scheduled_start_time_list,
                index=0,
            ),
        )
        .when(_.meeting_scheduled_start_time_count > 1)
        .then(None)  # Return None for ambiguous datetime values
        .otherwise(None)
    )
    meeting_scheduled_end_time_list: list[datetime] = F.array_distinct(
        arr=F.array_agg(_.call_data[_.meeting_scheduled_end_time]),
    )
    meeting_scheduled_end_time_count: int = F.cardinality(
        arr=_.meeting_scheduled_end_time_list,
    )
    meeting_scheduled_end_time: datetime | None = (
        F.when(_.meeting_scheduled_end_time_count == 1)
        .then(
            F.element_at(
                arr=_.meeting_scheduled_end_time_list,
                index=0,
            ),
        )
        .when(_.meeting_scheduled_end_time_count > 1)
        .then(None)  # Return None for ambiguous datetime values
        .otherwise(None)
    )
    meeting_scheduled_duration_list: list[int] = F.array_distinct(
        arr=F.array_agg(_.call_data[_.meeting_scheduled_duration_in_minutes]),
    )
    meeting_scheduled_duration_count: int = F.cardinality(
        arr=_.meeting_scheduled_duration_list,
    )
    meeting_scheduled_duration: int | None = (
        F.when(_.meeting_scheduled_duration_count == 1)
        .then(
            F.element_at(
                arr=_.meeting_scheduled_duration_list,
                index=0,
            ),
        )
        .when(_.meeting_scheduled_duration_count > 1)
        .then(-1)  # Return -1 for ambiguous int values
        .otherwise(None)
    )
    recording_duration_list: list[float] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.recording_duration_in_minutes]),
    )
    recording_duration_count: int = F.cardinality(arr=_.recording_duration_list)
    recording_duration_in_minutes: float = (
        F.when(_.recording_duration_count == 1)
        .then(
            F.element_at(
                arr=_.recording_duration_list,
                index=0,
            ),
        )
        .when(_.recording_duration_count > 1)
        .then(-1.0)  # Return -1.0 for ambiguous float values
        .otherwise(0)
    )
    recording_url_list: list[str] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.recording_url]),
    )
    recording_url_count: int = F.cardinality(arr=_.recording_url_list)
    recording_url: str | None = (
        F.when(_.recording_url_count == 1)
        .then(
            F.element_at(
                arr=_.recording_url_list,
                index=0,
            ),
        )
        .when(_.recording_url_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )
    transcript_plaintext_list: list[str] = F.array_distinct(
        arr=F.array_agg(expr=_.call_data[_.transcript_plaintext]),
    )
    transcript_plaintext_count: int = F.cardinality(arr=_.transcript_plaintext_list)
    transcript: str | None = (
        F.when(_.transcript_plaintext_count == 1)
        .then(
            F.element_at(
                arr=_.transcript_plaintext_list,
                index=0,
            ),
        )
        .when(_.transcript_plaintext_count > 1)
        .then("ambiguous")
        .otherwise(None)
    )

    llm_call_summary_general: P.PromptResponse = feature(
        max_staleness="infinity",
        expression=P.run_prompt("Fathom - Call summary - General"),
    )
    ai_call_summary_general: str = feature(
        max_staleness="infinity",
        expression=_.llm_call_summary_general.response,
    )

    llm_call_type: P.PromptResponse = P.completion(
        model="gpt-4.1",
        max_tokens=30000,
        temperature=0.1,
        top_p=0.1,
        messages=[
            P.message(
                role="user",
                content=F.jinja(prompt_meeting_type_user()),
            ),
        ],
        output_structure=StructuredOutputMeetingType,
    )
    ai_call_type: str = feature(
        max_staleness="infinity",
        cache_nulls=False,
        expression=F.json_value(
            _.llm_call_type.response,
            "$.meeting_type",
        ),
    )

    llm_call_insights_sales: P.PromptResponse = P.completion(
        model="gpt-4.1",
        max_tokens=30000,
        temperature=0.1,
        top_p=0.1,
        messages=[
            P.message(
                role="user",
                content=F.jinja(prompt_meeting_insights_sales_user()),
            ),
        ],
        output_structure=StructuredOutputCallInsights,
    )
    ai_reasons_for_meeting: str = feature(
        max_staleness="infinity",
        cache_nulls=False,
        expression=F.json_value(
            _.llm_call_insights_sales.response,
            "$.reasons_for_meeting",
        ),
    )
    ai_risk_flag: str = feature(
        max_staleness="infinity",
        cache_nulls=False,
        expression=F.json_value(
            _.llm_call_insights_sales.response,
            "$.risk_flag",
        ),
    )

    webhook_status_code: int
