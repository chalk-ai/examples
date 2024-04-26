"""An example of connecting Users to Credit Reports from a
third part API.

In this example, we are getting Credit Reports for our
users through a third part API. This example shows how
you can run arbitrary python code (and connect to third
party APIs in a python resolver.
"""

import os
import requests

from chalk import online

from chalk.features import features, has_many, DataFrame


@features
class CreditReport:
    report_id: str
    user_id: str
    # The raw report, which we'll save as a plain string
    # to parse and extract later.
    report: str


@features
class User:
    id: str
    first_name: str
    last_name: str
    # Adds the pii tag to the ssn feature (https://docs.chalk.ai/docs/feature-discovery#tags)
    # :tags: pii
    ssn: str
    city: str
    state: str
    credit_report: DataFrame[CreditReport] = has_many(lambda: CreditReport.user_id == User.id)


# Inject a secret through the Chalk dashboard (https://docs.chalk.ai/docs/env-vars)
url = os.getenv("MY_VENDOR_URL")


@online
def get_credit_report(
    first_name: User.first_name,
    last_name: User.last_name,
    city: User.city,
    state: User.state,
    id: User.id,
) -> CreditReport:
    """
    This resolver populates the credit report feature for a user by making a request to
    a third party API.
    """
    res = requests.get(
        f"{url}/transunion/credit-report",
        json={
            "firstName": first_name,
            "lastName": last_name,
            "city": city,
            "state": state,
        },
    ).json()
    return CreditReport(user_id=id, report_id=res["pdfReportId"], report=res["data"])
