"""Running Predictive Models in Chalk

In this example, we are using a logistic regression model to predict
whether a user will churn from our video streaming service. This example
assumes we have already trained a simple model on `age`, `num_friends` and
`viewed_minutes` features for a number of our users (a dummy model—
named `'churn_model.skops'`—can be found in this file's directory).
"""

from chalk.features import features
from chalk import online
import numpy as np
from skops.io import load
from functools import cached_property
from typing import List
import os


@features
class User:
    """This is a User for our streaming streaming platform. We keep track
    of a user's age, how many friends they have on our platform, and how
    many minutes of video they have viewed.
    """
    id: str
    age: int
    num_friends: int
    viewed_minutes: float
    # probability_of_churn is a feature that we predict
    # from a user's age, number of friends, and viewed_minutes.
    # We run this prediction in the 'get_user_churn_probability'
    # resolver below.
    probability_of_churn: float


class PredictionModel:
    """
    # Previously, we trained a model on our user data. This
    # model has been saved to our local chalk directory, next to
    # our feature and resolver code. When we run chalk apply
    # it will be incorporated into deployments.

    from sklearn.linear import LogisticRegression
    from skops.io import save

    X_train, y_train = ...

    model = LogisticRegression()
    model.fit(X_train, y_train)

    save(model, "churn_model.skops")
    """

    def __init__(self, filename: str):
        self.filename = filename

    @cached_property
    def _model(self):
        # The "TARGET_ROOT" environment variable is set by Chalk for both branch and
        # standard deployments. You can read more about it on our docs:
        # https://docs.chalk.ai/docs/env-vars#chalk-environment-variable
        filepath = os.path.join(os.environ.get("TARGET_ROOT"), self.filename)

        return load(filepath, trusted=True)

    def predict(self, data: np.array):
        return self._model.predict(data)


# the model has been trained and saved in local chalk directory
churn_model = PredictionModel("churn_model.skops")


@online
def get_user_churn_probability(
    age: User.age,
    num_friends: User.num_friends,
    viewed_minutes: User.viewed_minutes,
) -> User.probability_of_churn:
    """
    This resolver runs a model that has been trained on a user's age, num_friends
    and viewed_minutes. It returns a platform churn prediction.
    """
    return churn_model.predict(np.array([[age, num_friends, viewed_minutes]]))
