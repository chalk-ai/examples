from sagemaker.workflow.function_step import step

@step(
    name="model-evaluation",
    instance_type='ml.t3.medium',
    keep_alive_period_in_seconds=300,
)
def evaluate(model, xtest_path: str, ytest_path: str) -> dict:
    import json
    import numpy as np
    import pandas as pd
    from sklearn.metrics import (
        accuracy_score,
        auc,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_curve,
    )

    X_test = pd.read_parquet(xtest_path)
    y_test = pd.read_parquet(ytest_path)

    prediction_probabilities = model.predict_proba(X_test)
    predictions = np.argmax(prediction_probabilities, axis=1)

    acc = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=1)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)
    conf_matrix = confusion_matrix(y_test, predictions)
    fpr, tpr, _ = roc_curve(y_test, prediction_probabilities[:, 1])
    auc_value = auc(fpr, tpr)

    report_dict = {
        "binary_classification_metrics": {
            "accuracy": {"value": acc, "standard_deviation": "NaN"},
            "f1": {"value": f1, "standard_deviation": "NaN"},
            "precision": {"value": precision, "standard_deviation": "NaN"},
            "recall": {"value": recall, "standard_deviation": "NaN"},
            "confusion_matrix": {
                "0": {"0": int(conf_matrix[0][0]), "1": int(conf_matrix[0][1])},
                "1": {"0": int(conf_matrix[1][0]), "1": int(conf_matrix[1][1])},
            },
            "receiver_operating_characteristic_curve": {
                "false_positive_rates": list(fpr),
                "true_positive_rates": list(tpr),
            },
            "auc": {"value": auc_value, "standard_deviation": "NaN"},
        },
    }

    print(f"evaluation report: {json.dumps(report_dict, indent=2)}")
    return report_dict

