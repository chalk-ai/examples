
#THIS SHOUDL BE SOMETHING THAT USES MAX_STALENESS TO CALCULATE THINGS
import requests
from chalk.features import features, feature, has_many, DataFrame
@features
class User:
    id: str
    first_name: str
    last_name: str
    ssn: str = feature(tags="pii")
    city: str
    state: str
    credit_report: DataFrame[CreditReport] \
        = has_many(lambda: CreditReport.user_id == User.id)

@features
class CreditReport:
    report_id: str
    user_id: str
    # theres a BUNCH of stuff in here
    report: json

url: str = None
@before_all
def init_credit_vendor():
    url = os.getenv('MY_VENDOR_URL')

def get_credit_report(first_name: User.first_name, last_name: User.last_name,
                      city: User.city, state: User.state, id = User.id
    ) -> CreditReport:
    args = {
        "firstName": first_name,
        "lastName": last_name,
        "city": city,
        "state": state
        }
    res = requests.post(f"{url}/equifax/credit-report", args).json()

    return CreditReport(
        user_id=id,
        report_id=res["pdfReportId"],
        report=res["data"]
    )