from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.conditions import ConditionGreaterThan
from sagemaker.workflow.fail_step import FailStep
from steps.dataset import create_dataset
from steps.training import train
from steps.evaluate import evaluate
from steps.register import register
from .config import MIN_F1

xtrain_path, xtest_path, ytrain_path, ytest_path = create_dataset()

delayed_model = train(xtrain_path=xtrain_path, ytrain_path=ytrain_path)
delayed_evaluation = evaluate(model=delayed_model, xtest_path=xtest_path, ytest_path=ytest_path)
delayed_register = register(
    model=delayed_model,
    evaluation=delayed_evaluation,
    sample_data=xtest_path,
    sample_target=ytest_path
)

conditionally_register = ConditionStep(
    name="conditionally_register",
    conditions=[
        ConditionGreaterThan(
            # Output of the evaluate step must be json serializable
            # to be consumed in the condition evaluation
            left=delayed_evaluation["binary_classification_metrics"]["f1"]["value"],
            right=MIN_F1,
        )
    ],
    if_steps=[delayed_register],
    else_steps=[FailStep(name="Fail", error_message="Model performance is not good enough")],
)

pipeline_name = "Dummy-ML-Pipeline"
pipeline = Pipeline(
    name=pipeline_name,
    steps=[conditionally_register],
)
