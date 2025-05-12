import json
import textwrap

import google.generativeai as genai
from chalk import online
from chalk.features import Features, before_all

from src.denylist import Denylist
from src.emailage.client import emailage_client
from src.experian import ExperianClient
from src.models import CreditReport, Tradeline, Transaction, User

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")


@online
async def get_transaction_category(memo: Transaction.memo) -> Transaction.completion:
    return (
        model.generate_content(
            textwrap.dedent(
                f"""\
        Please return JSON for classifying a financial transaction
        using the following schema.

        {{"category": str, "is_nsf": bool, "clean_memo": str, "is_ach": bool}}

        All fields are required. Return EXACTLY one JSON object with NO other text.
        Memo: {memo}"""
            ),
            generation_config={"response_mime_type": "application/json"},
        )
        .candidates[0]
        .content.parts[0]
        .text
    )


@online
def parse_genai_transaction_info(
    completion: Transaction.completion,
) -> Features[
    Transaction.category,
    Transaction.is_nsf,
    Transaction.is_ach,
    Transaction.clean_memo,
]:
    """Parse out the structured outputs from the genai completion."""
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
def get_domain_name(email: User.email) -> User.domain_name:
    return email.split("@")[-1]


@online
def get_email_username(email: User.email) -> User.email_username:
    username = email.split("@")[0]
    if "gmail.com" in email:
        username = username.split("+")[0].replace(".", "")
    return username.lower()


@online
def email_in_denylist(
    email: User.email,
    username: User.email_username,
) -> User.denylisted:
    """Check if the user's email is in a fixed set of denylisted emails."""
    return email in denylist or username in denylist


@online
def get_email_age(email: User.email) -> User.emailage_response:
    """Get the email age and domain age from the Emailage API."""
    return emailage_client.get_email_score(email)


@online
def get_emailage_features(
    emailage_response: User.emailage_response,
) -> Features[User.email_age_days, User.domain_age_days]:
    """Parse the emailage response into the email and domain age."""
    parsed = json.loads(emailage_response)
    return User(
        email_age_days=parsed["emailAge"],
        domain_age_days=parsed["domainAge"],
    )


experian_client = ExperianClient("EXPERIAN_API_KEY")


@online
def get_credit_report(
    name: User.name,
    dob: User.dob,
) -> Features[User.credit_report.raw, User.credit_report.id]:
    """Fetch the credit report from Experian."""
    return experian_client.fetch_credit_report(name, dob)


@online
def get_tradelines(
    raw: CreditReport.raw,
) -> CreditReport.tradelines[
    Tradeline.id,
    Tradeline.balance,
    Tradeline.amount,
    Tradeline.amount_past_due,
    Tradeline.payment_amount,
]:
    """Parse the raw credit report into tradelines."""
    parsed = json.loads(raw)
    return CreditReport(
        tradelines=[
            Tradeline(
                id=tradeline["Id"],
                balance=tradeline["Balance"],
                amount=tradeline["Amount"],
                amount_past_due=tradeline["AmountPastDue"],
                payment_amount=tradeline["PaymentAmount"],
            )
            for tradeline in parsed["Tradelines"]
        ]
    )
