from sagemaker.workflow.function_step import step


TRAINING_FEATURES = [
    "transaction.amt",
    "transaction.customer.age",
    "transaction.customer.income",
    "transaction.customer.fico",
    "transaction.customer.transaction_sum_30m",
    "transaction.customer.transaction_sum_1h",
    "transaction.confirmed_fraud"
]

TARGET_FEATURE = "transaction.confirmed_fraud"


@step(
    name="create_dataset",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def create_dataset(test_size, run_bucket):
    from chalk.client import ChalkClient
    from sklearn.model_selection import train_test_split

    # a Chalk client id & client secret for a token with permission to create datasets
    # should be added to the sagemaker environment—these are passed automatically to the
    # ChalkClient but can also be explicitly passed as arguments.

    chalk_dataset = ChalkClient(
        # client_id=os.environ['CHALK_CLIENT_ID'],           # automatically loaded by the Chalk Client if in the environment
        # client_secret=os.environ['CHALK_CLIENT_SECRET']    # automatically loaded by the Chalk Client if in the environment
    ).offline_query(
        max_samples=100_000,  # reads 100,000 samples from the Chalk dataset
        output=TRAINING_FEATURES,
        dataset_name="transactions_fraud_model",
    )
    dataset = chalk_dataset.to_pandas()

    X_train, X_test, y_train, y_test = train_test_split(
        dataset.drop(columns=[TARGET_FEATURE]),  # X
        dataset[TARGET_FEATURE],  # y
        test_size=test_size
    )

    xtrain_path = f"{run_bucket}/input/X_train.parquet"
    xtest_path = f"{run_bucket}/input/X_test.parquet"
    ytrain_path = f"{run_bucket}/input/y_train.parquet"
    ytest_path = f"{run_bucket}/input/y_test.parquet"

    dataset.to_parquet(f"{run_bucket}/raw_data/data.parquet")
    X_train.to_parquet(xtrain_path)
    y_train.to_parquet(ytrain_path)
    X_test.to_parquet(xtest_path)
    y_test.to_parquet(ytest_path)
    return xtrain_path, xtest_path, ytrain_path, ytest_path
