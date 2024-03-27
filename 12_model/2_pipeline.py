from chalk import online, DataFrame
from chalk.features import embedding, features, Vector
import numpy as np
import pandas as pd
from skops.io import load
from functools import cached_property
from typing import Sequence


@features
class User:
    id: str
    age: int
    favorite_categories: Sequence[str]
    viewed_minutes: float
    location: str
    device: str
    purchases: DataFrame["UserPurchase"]
    processed_features: Sequence[float]
    model_prediction: float


class PreprocessingPipeline:
    """
    # Example of how to save a preprocessing pipeline
    from sklearn.pipeline import make_pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from skops.io import save

    X_train = pd.DataFrame(
        dict(
            age=[20, 30, 40],
            viewed_minutes=[100, 200, 300],
            favorite_categories=["cat1", "cat2", "cat1"],
            location=["loc1", "loc2", "loc1"],
        )
    )

    pipeline = make_pipeline(
        ColumnTransformer(
            [("fav_cats", OneHotEncoder(), ["favorite_categories"]), ("loc", OneHotEncoder(), ["location"])],
            remainder="passthrough",
        ),
        StandardScaler(),
    )
    X_train_p = pipeline.fit_transform(X_train)

    save(pipeline, "pipeline.skops")
    """

    def __init__(self, filename: str):
        self.filename = filename

    @cached_property
    def _prep(self):
        return load(self.filename, trusted=True)

    def predict(self, data: np.array):
        return self._prep.transform(data)


# preprocessing pipeline has been trained and saved in local chalk dir
preprocessing_pipeline = PredictionModel("preprocessing.skops")


class PredictionModel:
    """
    # Example of how to save train and save model
    from sklearn.ensemble import RandomForestRegressor
    from skops.io import save

    X_train_p = pipeline.fit_transform(X_train) # see above for pipeline
    model = RandomForestRegressor()
    model.fit(X_train_p, y_train)

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
    user_processed: User.processed_features,
) -> User.model_prediction:
    return model.predict(
        User.processed_features
    )


@online
def get_user_prediction_data(
    user_age: User.age,
    user_favorite_categories: User.favorite_categories,
    user_viewed_minutes: User.viewed_minutes,
    user_location: User.location,
) -> User.model_prediction:
    # make sure features are in same order as when the preprocessing pipeline was trained
    return preprocessing_pipeline.transform(
        pd.DataFrame(
            [[user_age, user_viewed_minutes, user_favorite_categories, user_location]],
            columns=["age", "viewed_minutes", "favorite_categories", "location"]
        )
    )
