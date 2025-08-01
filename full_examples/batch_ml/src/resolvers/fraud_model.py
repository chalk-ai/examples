import os
from chalk import DataFrame, offline
from src.models import Transaction
import onnxruntime as rt
from functools import cached_property
import numpy as np


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PredictionModel:
    """
    # Previously, we trained a model on our user data. This
    # model has been saved to our local chalk directory next to
    # our feature and resolver code. When we run chalk apply
    # it will be incorporated into deployments.

    from sklearn.linear import LogisticRegression

    X_train, y_train = ...

    model = LogisticRegression()
    model.fit(X_train, y_train)
    model
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.input_name = None
        self.output_name = None

    @cached_property
    def _model(self) -> rt.InferenceSession:
        # The "TARGET_ROOT" environment variable is set by Chalk for both branch and
        # standard deployments. You can read more about it on our docs:
        # https://docs.chalk.ai/docs/env-vars#chalk-environment-variable
        filepath = os.path.join(
            os.environ.get("TARGET_ROOT", ROOT_DIR), "models", self.filename
        )

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        try:
            session = rt.InferenceSession(filepath)
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model from {filepath}: {e}")

        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name

        return session

    def predict(self, data: np.array, target_class=1):
        return self._model.run([self.output_name], {self.input_name: data})[0]


# the model has been trained and saved in our local Chalk directory
# models/fraud_model.onnx
fraud_model = PredictionModel("fraud_model.onnx")


@offline
def run_fraud_model(
    features: DataFrame[
        Transaction.id,
        Transaction.amount,
        Transaction.user.time_since_last_transaction,
        Transaction.user.num_transactions["1d"],
        Transaction.user.num_transactions["10d"],
        Transaction.user.num_transactions["30d"],
        Transaction.user.num_distinct_merchants_transacted["1d"],
        Transaction.user.num_distinct_merchants_transacted["10d"],
        Transaction.user.num_distinct_merchants_transacted["30d"],
    ],
) -> DataFrame[Transaction.id, Transaction.is_fraud]:
    """Predict whether new transactions are fraudulent based on transaction and user data."""

    predictions = fraud_model.predict(
        features.to_pandas().astype(np.float32).drop(columns=[Transaction.id]).values,
    )

    return features[Transaction.id].with_columns({Transaction.is_fraud: predictions})
