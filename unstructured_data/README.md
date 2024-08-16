# Integrating with unstructured data

Chalk can take unstructured data from sources such as Gemini, ChatGPT, Claude
and any other APIs you rely on. You can convert this data into features that
will live along with the rest of your feature codebase, making it simple to
build models combining structured and unstructured data.

In this example, you will:
- Learn how to use an LLM to classify your card transaction data to determine its
  purchase category and other information
- Define features representing the structured results of the LLM response
- Define resolvers showing how to send the LLM request and parse it

## 1. Define features

First, we define features representing our users and their card transactions in
[models.py](https://github.com/chalk-ai/examples/blob/main/unstructured_data/src/models.py):

```python
default_completion = json.dumps(
    dict(
        category="unknown",
        is_nsf=False,
        is_ach=False,
        clean_memo="",
    )
)


@features
class Transaction:
    id: int
    amount: float
    memo: str

    # :tags: genai
    clean_memo: str

    # The User.id type defines our join key implicitly
    user_id: "User.id"
    user: "User"

    # The time at which the transaction was created for temporal consistency
    at: FeatureTime

    completion: str = feature(max_staleness="infinity", default=default_completion)

    category: str = "unknown"
    is_nsf: bool = False  # NSF: insufficient funds
    is_ach: bool = False  # ACH: direct deposit


@features
class User:
    # Features pulled from Postgres for the user
    id: int
    email: str
    name: str
    dob: date

    # Whether the user appears in a denylist in s3
    denylisted: bool

    # The transactions, linked by the User.id type on the Transaction.user_id field
    transactions: DataFrame[Transaction]

    # The number of payments made by the user in the last 1, 7, and 30 days
    # Uses the category pulled from Gemini to count payments
    count_payments: Windowed[int] = windowed(
        "1d", "7d", "30d",
        expression=_.transactions[
            _.amount,
            _.at >= _.chalk_window,
            _.category == "payment"
        ].count(),
    )
```

## 2. Define LLM resolvers
In the rest of this readme, we will focus on the LLM-dependent features:
`completion`, `clean_memo`, `category`, `is_nsf`, and `is_ach`. (You can check
out the full code and our documentation to see how we resolve the rest of the
features using [SQL file
resolvers](https://docs.chalk.ai/docs/sql#sql-file-resolvers) and [windowed
aggregations](https://docs.chalk.ai/docs/aggregations).)

It's time to define how we want to prompt the LLM of our choice in
[resolvers.py](https://github.com/chalk-ai/examples/blob/main/unstructured_data/src/resolvers.py)!

```python
import google.generativeai as genai

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

@online
async def get_transaction_classification(memo: Transaction.memo) -> Transaction.completion:
    return model.generate_content(
        textwrap.dedent(
            f"""\
        Please return JSON for classifying a financial transaction
        using the following schema.

        {{"category": str, "is_nsf": bool, "clean_memo": str, "is_ach": bool}}

        All fields are required. Return EXACTLY one JSON object with NO other text.
        Memo: {memo}"""
        ),
        generation_config={"response_mime_type": "application/json"},
    ).candidates[0].content.parts[0].text
```

`Transaction.completion` represents the raw response from the LLM before parsing.
We store the response as its own feature so that we don't have to resend
requests to the LLM, but we can still separately iterate on how we parse and
convert it into downstream features.

Now that we have a feature representing the LLM response, we can define another
resolver that depends on it by taking it as a parameter:


```python
@online
def get_structured_outputs(completion: Transaction.completion) -> Features[
    Transaction.category,
    Transaction.is_nsf,
    Transaction.is_ach,
    Transaction.clean_memo,
]:
    body = json.loads(completion)
    return Transaction(
        category=body["category"],
        is_nsf=body["is_nsf"],
        is_ach=body["is_ach"],
        clean_memo=body["clean_memo"],
    )
```

In this resolver, we assume the LLM gives us a well-formed JSON response. We
retrieve the `category`, `is_nsf`, `is_ach`, and `clean_memo` features from the
JSON response.

There you have it! Once you deploy this code with Chalk, you're ready to
super-charge your machine learning by using structured data for traditional
features combined with LLM data where it shines.

