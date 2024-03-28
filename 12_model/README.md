# Modeling

With Chalk, it's easy to run models in resolvers.

## 1. Models

Models can be run as part of resolvers.

**[1_model.py](1_model.py)**

```python
class PredictionModel:
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
        age: User.age, num_friends: User.num_friends, User.viewed_minutes,
) -> User.model_prediction:
    return model.predict(
        User.age, User.num_friends, User.viewed_minutes
    )
```

## 2. Pipelines

Pipelines can be run as part of resolvers: this means you can save processed features in your offline store.

**[2_pipeline.py](2_pipeline.py)**

```python
class PreprocessingPipeline:
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
```
