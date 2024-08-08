from sagemaker.workflow.function_step import step


@step(
    name="model_registration",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def register(
    model,
    sample_data: str,
    eval_source_s3: str,
    model_package_group: str,
    model_approval_status: str
) -> str:
    import pandas as pd
    from sagemaker import MetricsSource, ModelMetrics
    from sagemaker.serve.builder.model_builder import ModelBuilder
    from sagemaker.serve.builder.schema_builder import SchemaBuilder

    # Create model_metrics as per evaluation report in s3
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=eval_source_s3,
            content_type="application/json",
        )
    )

    sample_data = pd.read_parquet(sample_data, nrows=10)

    schema_builder = SchemaBuilder(
        sample_input=sample_data.to_numpy(),
        sample_output=model.predict(sample_data),
    )

    # Build the trained model and register it
    model_builder = ModelBuilder(
        model=model,
        schema_builder=schema_builder,
    )

    model_package = model_builder.build().register(
        model_package_group_name=model_package_group,
        approval_status=model_approval_status,
        model_metrics=model_metrics,
    )

    return model_package.model_package_arn
