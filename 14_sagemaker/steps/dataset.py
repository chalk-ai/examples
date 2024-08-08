# import os

from chalk.client import ChalkClient
from sagemaker.workflow.function_step import step
from ..config import RUN_BUCKET, TRAINING_FEATURES, TARGET_FEATURE, STRATIFY_FEATURE, test_size


# check that the inputs are valid

@step(
    name="create_dataset",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def create_dataset(test_size):
    from sklearn.model_selection import train_test_split

    # a Chalk client id & client secret for a token with permission to create datasets
    # should be added to the sagemaker environment—these are passed automatically to the
    # ChalkClient but can also be exlicitly passed as arguments.

    chalk_dataset = ChalkClient(
        # client_id=os.environ['CHALK_CLIENT_ID'],           # automatically loaded by the Chalk Client but expected
        # client_secret=os.environ['CHALK_CLIENT_SECRET']        # automatically loaded by the Chalk Client but expected
    ).offline_query(
        max_samples=100_000,  # reads 100,000 samples from the Chalk dataset
        output=TRAINING_FEATURES,
        wait=True
    )
    dataset = chalk_dataset.to_pandas()
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.drop(columns=[TARGET_FEATURE]),  # X
        dataset[TARGET_FEATURE],  # y
        test_size=test_size,
        stratify=None if STRATIFY_FEATURE is None else dataset[STRATIFY_FEATURE]
    )

    xtrain_path = f"{RUN_BUCKET}/input/X_train.parquet"
    ytrain_path = f"{RUN_BUCKET}/input/y_train.parquet"
    xtest_path = f"{RUN_BUCKET}/input/X_test.parquet"
    ytest_path = f"{RUN_BUCKET}/input/y_test.parquet"

    dataset.to_parquet(f"{RUN_BUCKET}/raw_data/data.parquet")
    X_train.to_parquet(xtrain_path)
    y_train.to_parquet(ytrain_path)
    X_test.to_parquet(xtest_path)
