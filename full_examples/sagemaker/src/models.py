from datetime import date
from dateutil.relativedelta import relativedelta
from chalk import online, DataFrame, FeatureTime, Windowed, _, feature, windowed
from chalk.features import features


@features
class Transaction: 
    id: int
    amt: float
    confirmed_fraud: bool
    customer_id: "Customer.id"
    customer: "Customer"

    # The time at which the transaction was created for temporal consistency
    at: FeatureTime


@features
class Customer:
    id: int
    name: str
    email: str
    dob: date
    age: int
    income: int
    fico: int

    # The transactions, linked by the Customer.id type on the Transaction.customer_id field
    transactions: DataFrame[Transaction]

    transaction_sum: Windowed[float] = windowed(
        "30m",
        "1h",
        default=0,
        expression=_.transactions[_.amount, _.ts > _.chalk_window].sum(),
    )


@online
async def get_fico(email: Customer.email) -> Customer.fico:
    # Use your preferred FICO score API here
    ...

@online
async def get_age(Customer.dob) -> Customer.age:
    return relativedelta(end_date, start_date).years

