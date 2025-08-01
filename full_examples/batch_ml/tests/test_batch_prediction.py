from chalk import DataFrame
from datetime import datetime, timedelta
from src.resolvers.fraud_model import run_fraud_model
from src.models import User, Transaction

# Chalk provides a simple interface for unit tests that works with
# pytest or any other python testing framework: https://docs.chalk.ai/docs/unit-tests
# since chalk resolvers are just python functions, you can test them
# just like you'd unit test any other python function.


def test_fraud_model():
    # call the python resolver and assert the result
    input = DataFrame(
        {
            Transaction.id: [1, 2, 3, 4],
            Transaction.amount: [10, 100, 50, 200],
            Transaction.user.time_since_last_transaction: [
                timedelta(days=30).total_seconds(),
                timedelta(days=10).total_seconds(),
                timedelta(days=5).total_seconds(),
                timedelta(days=60).total_seconds(),
            ],
            Transaction.user.num_transactions["1d"]: [1, 0, 2, 0],
            Transaction.user.num_transactions["10d"]: [5, 2, 6, 0],
            Transaction.user.num_transactions["30d"]: [10, 4, 12, 1],
            Transaction.user.num_distinct_merchants_transacted["1d"]: [1, 0, 2, 0],
            Transaction.user.num_distinct_merchants_transacted["10d"]: [2, 1, 3, 0],
            Transaction.user.num_distinct_merchants_transacted["30d"]: [3, 2, 4, 1],
        }
    )
    result = run_fraud_model(input)
    assert isinstance(result, DataFrame)
    assert len(result) == 4
