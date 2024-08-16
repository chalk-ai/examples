import json
import textwrap

import google.generativeai as genai
from chalk import online
from chalk.features import Features, before_all
from src.denylist import Denylist

from src.models import Transaction, User

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")


@online
async def get_transaction_category(memo: Transaction.memo) -> Transaction.completion:
    """Here, we pull out the raw response from calling out to Gemini.
    The feature `Transaction.completion` is a string, but we can use the
    `get_structured_outputs` function to convert it to a structured output.

    Transaction.completion has max-staleness of infinity, so we won't need
    to recompute the completion, but can still iterate on how we parse it.
    """

    return model.generate_content(
        textwrap.dedent(
            f"""\
        Please return JSON for classifying a financial transaction
        using the following schema.

        {{"category": str, "is_nsf": bool, "clean_memo": str, "is_ach": bool}}

        All fields are required. Return EXACTLY one JSON object with NO other text.
        Memo: {memo}"""
        ),
        generation_config={"response_mime_type": "application/json"},
    ).candidates[0].content.parts[0].text


@online
def get_structured_outputs(completion: Transaction.completion) -> Features[
    Transaction.category,
    Transaction.is_nsf,
    Transaction.is_ach,
    Transaction.clean_memo,
]:
    """Given the completion, we parse it into a structured output."""
    body = json.loads(completion)
    return Transaction(
        category=body["category"],
        is_nsf=body["is_nsf"],
        is_ach=body["is_ach"],
        clean_memo=body["clean_memo"],
    )


denylist = Denylist(source="gs://socure-data/denylist.csv")


@before_all
def init_denylist():
    denylist.load()


@online
def email_in_denylist(email: User.email) -> User.denylisted:
    return email in denylist
