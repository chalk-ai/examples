from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
    ParameterFloat,
)
from uuid import uuid4

BUCKET_PREFIX = "s3://chalk-sagemaker-models/"
RUN_ID = uuid4()
MODEL_PACKAGE_GROUP = "chalk-sagemaker-xgb"
RUN_BUCKET = f"s3://chalk-sagemaker-models/{MODEL_PACKAGE_GROUP}/{RUN_ID}/"

mse_threshold = ParameterFloat(name="MseThreshold", default_value=6.0)
test_size = ParameterFloat(name="TestSize", default_value=0.2)

TRAINING_FEATURES = [
    "transaction.amt",
    "transaction.merchant_id",
    "transaction.date",
    "transaction.category",
    "transaction.customer.transaction_sum_30m",
    "transaction.customer.transaction_sum_1h",
]

TARGET_FEATURE = "transaction.confirmed_fraud"

STRATIFY_FEATURE = "transaction.merchant_id"

MIN_F1 = 0.8

# small validatity checks
assert STRATIFY_FEATURE is None or STRATIFY_FEATURE in TRAINING_FEATURES, f"straify feature '{STRATIFY_FEATURE}' not in training features: {TRAINING_FEATURES}."
assert TARGET_FEATURE in TRAINING_FEATURES, f"target feature '{TARGET_FEATURE}' not in training features: {TRAINING_FEATURES}."
