from ..config import RUN_BUCKET, MODEL_PACKAGE_GROUP

@step(
    name="model_registration",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def register(model, evaluation, sample_data, sample_target):
    import json
    import numpy as np
    import pandas as pd
    import s3fs
    from pathlib import Path
    from sagemaker import MetricsSource, ModelMetrics
    from sagemaker.serve.builder.model_builder import ModelBuilder
    from sagemaker.serve.builder.schema_builder import SchemaBuilder
    from sagemaker.serve.spec.inference_spec import InferenceSpec
    from sagemaker.utils import unique_name_from_base

    class XGBoostSpec(InferenceSpec):
        def load(self, model_dir: str):
            model = XGBClassifier()
            model.load_model(model_dir + "/xgboost-model")
            return model

        def invoke(self, input_object: object, model: object):
            prediction_probabilities = model.predict_proba(input_object)
            predictions = np.argmax(prediction_probabilities, axis=1)
            return predictions

    # Upload evaluation report to s3
    eval_file_name = unique_name_from_base("evaluation")
    eval_report_s3_uri = (
        f"s3://{bucket}/{model_package_group_name}/evaluation-report/{eval_file_name}.json"
    )
    s3_fs = s3fs.S3FileSystem()
    eval_report_str = json.dumps(evaluation)
    with s3_fs.open(eval_report_s3_uri, "wb") as file:
        file.write(eval_report_str.encode("utf-8"))

    # Create model_metrics as per evaluation report in s3
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=eval_report_s3_uri,
            content_type="application/json",
        )
    )

    sample_data = pd.read_csv(sample_data, nrows=10)
    sample_data.pop(label_column)

    schema_builder = SchemaBuilder(
        sample_input=sample_data.to_numpy(),
        sample_output=model.predict(sample_data),
    )

    model_path = Path("/tmp/model/")
    model_path.mkdir(parents=True, exist_ok=True)
    model.save_model(model_path / "xgboost-model")

    # Build the trained model and register it
    model_builder = ModelBuilder(
        model_path=str(model_path),
        inference_spec=XGBoostSpec(),
        schema_builder=schema_builder,
        role_arn=role,
        s3_model_data_url=f"s3://{bucket}/{model_package_group_name}/model-artifacts",
    )
    model_package = model_builder.build().register(
        model_package_group_name=MODEL_PACKAGE_GROUP,
        approval_status=model_approval_status,
        model_metrics=model_metrics,
    )

    print(f"Registered Model Package ARN: {model_package.model_package_arn}")
    return model_package.model_package_arn
