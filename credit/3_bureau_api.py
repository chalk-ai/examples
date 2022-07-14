import os
import requests

from chalk import realtime

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
    # :tags: pii
    ssn: str
    city: str
    state: str
    credit_report: DataFrame[CreditReport] = has_many(lambda: CreditReport.user_id == User.id)


# Inject a secret through the Chalk dashboard
url = os.getenv("MY_VENDOR_URL")


@realtime
def get_credit_report(
    first_name: User.first_name,
    last_name: User.last_name,
    city: User.city,
    state: User.state,
    id: User.id,
) -> CreditReport:
    res = requests.post(
        f"{url}/transunion/credit-report",
        json={
            "firstName": first_name,
            "lastName": last_name,
            "city": city,
            "state": state,
        },
    ).json()
    return CreditReport(user_id=id, report_id=res["pdfReportId"], report=res["data"])
