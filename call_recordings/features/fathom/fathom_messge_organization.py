import os

import polars as pl
from chalk.features import before_all, online
from chalk.logging import chalk_logger
from openai import OpenAI
from pydantic import BaseModel

from src.fathom.features.fathom_feature_set import FathomCallData, FathomMessage

client: OpenAI | None = None


def prompt_fathom_message_organization_user(
    attendee_mapping: str,
    speaker: str,
) -> str:
    return f"""You are tasked with matching a speaker name to their organization domain based on call attendee data.

    Speaker to match: "{speaker}"

    Attendee data:
    {attendee_mapping}

    Please analyze the speaker name and match it to one of the attendee names listed above. Consider:
    - Exact name matches
    - Partial name matches (first name, last name, or nicknames)
    - Common variations or abbreviations
    - Case-insensitive matching

    Return only the matching domain (e.g., "company.com") if you find a match, or "unknown" if no reasonable match can be determined.

    /{{
        "domain": string
    /}}
    """


def is_completion_response_null_check(
    completion_response,
) -> BaseModel | None:
    if completion_response is None:
        chalk_logger.error(
            msg="No completion returned from OpenAI.",
        )
        return None

    if completion_response.choices is None:
        chalk_logger.error(
            msg="No choices returned from OpenAI.",
        )
        return None

    if completion_response.choices[0].message.parsed is None:
        chalk_logger.error(
            msg="No parsed message returned from OpenAI.",
        )
        return None

    parsed_response: BaseModel = completion_response.choices[0].message.parsed
    return parsed_response


@before_all
def init_client() -> None:
    global client
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    chalk_logger.info(
        msg="Initializing OpenAI client...",
    )


@online
def get_speaker_domain_from_attendees(
    call_data: FathomMessage.call.call_data[
        FathomCallData.company_domain,
        FathomCallData.attendee_name,
    ],
    speaker: FathomMessage.speaker,
) -> FathomMessage.organization_etl:
    df: pl.DataFrame = call_data.to_polars().collect()
    attendee_mapping: str = "\n".join(
        [
            f"Attendee '{row[1]}' belongs to the domain '{row[0]}'."
            for row in df.iter_rows()
        ],
    )

    def fetch_chat_response(
        system_prompt: str | None,
        user_prompt: str,
        base_model: type[BaseModel],
    ) -> BaseModel | None:
        messages: list[dict[str, str]] = [
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
        if system_prompt is not None:
            messages.insert(0, {"role": "system", "content": system_prompt})

        completion_response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=base_model,
        )
        return is_completion_response_null_check(completion_response)

    class StructuredOutput(BaseModel):
        domain: str

    response: StructuredOutput | None = fetch_chat_response(
        system_prompt=None,
        user_prompt=prompt_fathom_message_organization_user(
            attendee_mapping=attendee_mapping,
            speaker=speaker,
        ),
        base_model=StructuredOutput,
    )

    if response is not None and response.domain.lower() != "unknown":
        return response.domain

    return None
