from sagemaker.workflow.pipeline import Pipeline
from steps.dataset import create_dataset
from steps.training import train
from steps.evaluate import evaluate
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
    ParameterFloat,
)
from uuid import uuid4

BUCKET_PREFIX = "s3://chalk-sagemaker-models/"

if __name__ == "__main__":
    # Create Run Parameters
    model_package_group = "chalk-sagemaker-xgb"
    run_bucket = f"s3://chalk-sagemaker-models/{model_package_group}/{uuid4()}/"

    # Required F1 Threshold for model registration
    f1_threshold = ParameterFloat(name="F1Threshold", default_value=0.8)

    # Size of test split
    test_size = ParameterFloat(name="TestSize", default_value=0.2)

    # Number of estimators to evaluate
    num_rounds = ParameterInteger(name="NumRounds", default_value=50)
    run_bucket = ParameterString(name="RunBucket", default_value=run_bucket)
    model_package_group = ParameterString(name="ModelPackageGroup", default_value="chalk-sagemaker-xgb")


    # Instantiate Steps
    delayed_data = create_dataset(test_size=test_size, run_bucket=run_bucket)
    delayed_model = train(xtrain_path=delayed_data[0], ytrain_path=delayed_data[2], num_rounds=num_rounds)
    delayed_evaluation = evaluate(model=delayed_model, xtest_path=delayed_data[1], ytest_path=delayed_data[3], run_bucket=run_bucket)

    # Create Pipeline
    pipeline = Pipeline(
        name="ChalkaiSagemakerPipeline",
        steps=[delayed_evaluation],
        parameters=[
            f1_threshold,
            test_size,
            run_bucket,
            model_package_group,
            num_rounds,
        ]
    )
