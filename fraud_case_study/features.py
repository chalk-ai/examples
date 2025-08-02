from chalk.features import features, FeatureTime
from chalk.streams import Windowed, windowed


@features
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    address: str
    country_of_residence: str

    # these features are aggregated over the last 7, 30, and 90 days
    avg_txn_amount: Windowed[float] = windowed("7d", "30d", "90d")
    num_overdrafts: Windowed[int] = windowed("7d", "30d", "90d")

    risk_score: float

    # transactions consists all Transaction rows that are joined to User
    # by transaction.user_id
    transactions: DataFrame["Transaction"]


@features
class Transaction:
    # these features are loaded directly from the kafka data source
    id: int
    user_id: User.id
    ts: FeatureTime
    vendor: str
    description: str
    amount: float
    country: string
    is_overdraft: bool

    # we compute this feature using transaction.country and transaction.user.country_of_residence
    in_foreign_country: bool = _.country == _.user.country_of_residence





