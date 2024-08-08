import os

from sagemaker.workflow.function_step import step
from ..config import RUN_BUCKET, TRAINING_FEATURES, TARGET_FEATURE, STRATIFY_FEATURE, test_size


use_gpu = False
param = dict(
    objective="binary:logistic",
    max_depth=5,
    eta=0.2,
    gamma=4,
    min_child_weight=6,
    subsample=0.7,
    tree_method="gpu_hist" if use_gpu else "hist",  # Use GPU accelerated algorithm
)
num_round = 50


@step(
    name="model-training",
    instance_type="ml.m5.xlarge",
    keep_alive_period_in_seconds=300,
)
def train(
    xtrain_path: str,
    ytrain_path: str,
    param: dict = param,
    num_round: int = num_round,
):
    from sklearn.pipeline import Pipeline
    import pandas as pd
    from xgboost import XGBClassifier

    # read data files from S3
    X_train = pd.read_parquet(xtrain_path)
    y_train = pd.read_parquet(ytrain_path)

    # create dataframe and label series
    y_train = (train_df.pop(label_column) == "M").astype("int")
    y_validation = (validation_df.pop(label_column) == "M").astype("int")

    xgb = XGBClassifier(n_estimators=num_round, **param)
    xgb.fit(
        train_df,
        y_train,
        eval_set=[(validation_df, y_validation)],
        early_stopping_rounds=5,
    )
