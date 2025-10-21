import os

from chalk.features import Features, before_all, online
from chalk.logging import chalk_logger
from openai import OpenAI
from pydantic import BaseModel
import requests

from src.marketplace import (
    Item,
    Seller,
    User,
)
from src.marketplace.item_category.item_category_value_enum import ItemCategoryValueEnum
from src.marketplace.item_category.item_category_value_llm_prompts import (
    prompt_item_category_value_system,
    prompt_item_category_value_user,
)

client: OpenAI | None = None


@before_all
def init_client() -> None:
    global client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chalk_logger.info(msg="Initializing OpenAI client...")

    global salesforce_access_token
    salesforce_access_token = os.getenv("SALESFORCE_ACCESS_TOKEN")

    global salesforce_instance_url
    salesforce_instance_url = os.getenv("SALESFORCE_INSTANCE_URL")


@online
def get_item_category_value(
    item_title: Item.title,
) -> Features[
    Item.genre_from_llm,
    Item.genre_from_llm_confidence,
    Item.genre_from_llm_reasoning,
]:
    def fetch_chat_response(
        system_prompt: str,
        user_prompt: str,
        base_model: type[BaseModel],
    ) -> BaseModel | None:
        completion_response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format=base_model,
        )
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

    system_prompt: str = prompt_item_category_value_system()
    user_prompt: str = prompt_item_category_value_user(
        book_title=item_title,
    )

    class StructuredOutput(BaseModel):
        genre: ItemCategoryValueEnum
        confidence_score: float
        reasoning: str

    structured_ouput: StructuredOutput | None = fetch_chat_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        base_model=StructuredOutput,
    )
    if structured_ouput is not None:
        return Item(
            genre_from_llm=structured_ouput.genre,
            genre_from_llm_confidence=structured_ouput.confidence_score,
            genre_from_llm_reasoning=structured_ouput.reasoning,
        )

    return Item(
        genre=None,
        genre_confidence_score=None,
        genre_reasoning=None,
    )


@online
def get_seller_username(
    email: Seller.email,
) -> Seller.username:
    username = email.split("@")[0]
    if "gmail.com" in email:
        username = username.split("+")[0].replace(".", "")

    return username.lower()


@online
def get_user_data_from_crm(
    contact_id: User.id,
) -> Features[
    User.phone,
    User.account_name,
    User.salesforce_lookup_success,
]:
    # we can actually parse this function and run the equivalent but in C++
    # https://docs.chalk.ai/docs/static-resolver-optimization
    # we'll rebuild the function but using chalk expressions e.g. https://docs.chalk.ai/api-docs#http_request
    endpoint = f"{salesforce_instance_url}/services/data/v59.0/sobjects/Contact/{contact_id}"
    headers = {
        "Authorization": f"Bearer {salesforce_access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        contact_data = response.json()
        return User(
            phone=contact_data.get("Phone"),
            account_name=contact_data.get("Account", {}).get("Name") if contact_data.get("Account") else None,
            salesforce_lookup_success=True,
        )

    return User(
        phone=None,
        account_name=None,
        salesforce_lookup_success=False,
    )
