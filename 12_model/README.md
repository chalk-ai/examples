# Modeling

With Chalk, it's easy to run models in resolvers.

## 1. Models
The example code below shows how to integrate a predictive model into a resolver.

**[1_model.py](1_model.py)**

```python
class PredictionModel:
    """
    # Previously, we trained a model on our user data. This
    # model has been saved to our local chalk directory next to
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

    def predict(self, data: np.array, target_class=1):
        # predict proba returns something like [.2, .8] which is the probability of
        # the 0 class and 1 class, respectively. We want to return the probability
        # of class 1.
        class_prediction_probabilities = {
            class_: prob
            for class_, prob in zip(self._model.classes_, self._model.predict_proba(data).squeeze(), strict=True)
        }
        return class_prediction_probabilities[target_class].item()  # item converts numpy array to float


# the model has been trained and saved in our local Chalk directory
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
```

## 2. OpenAI

Chalk also makes it easy to integrate LLMs like ChatGPT, into your resolvers. In the
following example, we use Chat-GPT to answer questions about our Users.

Additionally, since our questions are often repeated, we cache the results of the queries,
limiting the number of API requests we need to make.

The example code below shows how to run a API request in a python resolver:

**[2_openai.py](2_openai.py)**

```python
# run queries by the hash of the prompt
@online
def get_openai_answer(
        prompt_hash: OpenAiQuery.prompt_hash,
        prompt: OpenAiQuery.prompt,
) -> OpenAiQuery.prompt_result:
    result = openai_client.chat.completions.create(
        messages=[
            {
                'role': 'user',
                'content': prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return OpenAiQueryResult(
        id=prompt_hash,
        result=result.choices[0].message.content,
    )
```
