## Codegen with Chalk

If you’re working with external ML models or microservices, it can be helpful to generate
boilerplate code for calling those services—especially when those models operate on Chalk
features.

In this folder, the file `custom_model.py` defines a class `CustomModel`, that when created,
stores the information it needs to render the resolver definition for an HTTP call to a
service hosting a model score.

```python
CustomModel(
    url="https://internal.example.com/model1",
    dependencies={
        "nms": User.name_match_score,
        "email": User.email,
    },
    computes=User.score1,
)
```

The file `models.py` when executed overwrites the `score_resolvers.py` file with the
auto-generated definitions of the custom model:

```python
@online
def get_score1(nms: User.name_match_score, email: User.email) -> User.score1:
    response = requests.post(
        "https://internal.example.com/model1",
        headers={"accept": "application/json"},
        json={"nms": nms, "email": email},
    )
    return response.json().get("prediction")
```

If you find yourself repeating the same pattern for many of these resolvers, codegen
can be helpful to dry up your definitions.