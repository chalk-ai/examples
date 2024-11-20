from chalk import online, DataFrame
from kafka_resolver import TransactionMessage
from risk import riskclient


@online
def get_avg_txn_amount(txns: DataFrame[TransactionMessage]) -> DataFrame[User.id, User.avg_txn_amount]:
    # we define a simple aggregation to calculate the average transaction amount
    # using SQL syntax (https://docs.chalk.ai/docs/aggregations#using-sql)
    # the time filter is pushed down based on the window definition of the feature
    return f"""
       select
         user_id as id,
         avg(amount) as avg_txn_amount
       from {txns}
       group by 1
   """

@online
def get_num_overdrafts(txns: DataFrame[TransactionMessage]) -> DataFrame[User.id, User.num_overdrafts]:
    # we define a simple aggregation to calculate the number of overdrafts
    # using SQL syntax (https://docs.chalk.ai/docs/aggregations#using-sql)
    # the time filter is pushed down based on the window definition of the feature
    return f"""
       select
         user_id as id,
         count(*) as num_overdrafts
       from {txns}
       where is_overdraft = 1
       group by 1
   """

@online
def get_risk_score(
    first_name: User.first_name,
    last_name: User.last_name,
    email: User.email,
    address: User.address
) -> User.risk_score:
    # we call our internal Risk API to fetch a user's latest calculated risk score
    # based on their personal information
    riskclient = riskclient.RiskClient()
    return riskclient.get_risk_score(first_name, last_name, email, address)

