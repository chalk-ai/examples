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
        return load(
          os.path.join(
            os.environ.get('TARGET_ROOT'),
            self.filename
          ),
          trusted=True
        )

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
