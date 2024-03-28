from chalk.features import features
from chalk import online
import numpy as np
from skops.io import load
from functools import cached_property
from typing import Sequence


@features
class User:
    id: str
    age: int
    num_friends: int
    favorite_categories: Sequence[str]
    viewed_minutes: float
    location: str
    model_prediction: float


class PredictionModel:
    """
    from sklearn.ensemble import RandomForestRegressor
    from skops.io import save

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    save(model, "model.skops")
    """

    def __init__(self, filename: str):
        self.filename = filename

    @cached_property
    def _model(self):
        return load(self.filename, trusted=True)

    def predict(self, data: np.array):
        return self._model.predict(data)


# model has been trained and saved in local chalk directory
model = PredictionModel("model.skops")


@online
def get_model_prediction(
    age: User.age, num_friends: User.num_friends, viewed_minutes: User.viewed_minutes,
) -> User.model_prediction:
    return model.predict(
        np.array([[age, num_friends, viewed_minutes]])
    )
