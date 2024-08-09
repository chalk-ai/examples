from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.conditions import ConditionGreaterThan
from sagemaker.workflow.fail_step import FailStep
from steps.dataset import create_dataset
from steps.training import train
from steps.evaluate import evaluate
from steps.register import register
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
    model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="PendingManualApproval")

    # Instantiate Steps
    delayed_data = create_dataset(test_size=test_size, run_bucket=run_bucket)
    delayed_model = train(xtrain_path=delayed_data[0], ytrain_path=delayed_data[2], num_rounds=num_rounds)
    delayed_evaluation = evaluate(model=delayed_model, xtest_path=delayed_data[1], ytest_path=delayed_data[3], run_bucket=run_bucket)
    delayed_register = register(
        model=delayed_model,
        sample_data=delayed_data[2],
        model_package_group=model_package_group,
        model_approval_status=model_approval_status,
        eval_source_s3=delayed_evaluation
    )

    conditionally_register = ConditionStep(
        name="conditionally_register",
        conditions=[
            ConditionGreaterThan(
                left=delayed_evaluation["f1"],
                right=f1_threshold,
            )
        ],
        if_steps=[delayed_register],
        else_steps=[
            FailStep(
                name="fail",
                error_message=(
                    f"Model performance  is not greater than required f1 threshold"
                )
            )
        ],
    )

    # Create Pipeline
    pipeline = Pipeline(
        name="ChalkaiSagemakerPipeline",
        steps=[conditionally_register],
        parameters=[
            f1_threshold,
            test_size,
            run_bucket,
            model_package_group,
            model_approval_status,
            num_rounds,
        ]
    )
