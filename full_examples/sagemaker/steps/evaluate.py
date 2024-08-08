from sagemaker.workflow.function_step import step

@step(
    name="model-evaluation",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def evaluate(model, xtest_path: str, ytest_path: str, run_bucket: str) -> dict:
    import pandas as pd
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
    )
    import s3fs
    import json

    X_test = pd.read_parquet(xtest_path)
    y_test = pd.read_parquet(ytest_path)

    predictions = model.predict(X_test)

    results = {
        "accuracy": accuracy_score(y_test, predictions),
        "f1": f1_score(y_test, predictions),
        "precision": precision_score(y_test, predictions),
        "recall": recall_score(y_test, predictions),
    }

    # Upload evaluation report to s3
    s3_fs = s3fs.S3FileSystem()

    with s3_fs.open(f"{run_bucket}/evaluation/evaluation.json", "wb") as file:
        file.write(json.dumps(results).encode("utf-8"))

    return results

