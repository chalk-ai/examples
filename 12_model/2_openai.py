from chalk import online
from chalk.features import features, has_many, DataFrame, has_one, before_all

from openai import OpenAI

import hashlib
import os

openai_client: OpenAI

@before_all
def initialize_open_ai_client():
    # Note, one should be cautious when using global to give access to custom
    # data sources: https://docs.chalk.ai/docs/generic#scopes
    global openai_client
    openai_client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OAK"),
    )

prompts = dict(
    is_exec="Does the job title `{title}` mean that the person is a executive at their company?"
)


@features(max_staleness="100d")
class OpenAiQueryResult:
    id: str
    result: str

@features
class OpenAiQuery:
    id: str
    user_id: str
    # this is one of `is_exec`, `other_quest`, random_question (it is is the question "type")
    category: str
    prompt: str
    prompt_hash: str
    prompt_result: OpenAiQueryResult = has_one(lambda: OpenAiQuery.prompt_hash==OpenAiQueryResult.id)

@features
class User:
    id: str
    title: str
    is_exec: bool
    open_ai_queries: DataFrame[OpenAiQuery] = has_many(lambda: User.id==OpenAiQuery.user_id)

@online
def get_exec_query(
    user_id: User.id,
    title: User.title,
) -> User.open_ai_queries:
    prompt = prompts["is_exec"].format(title=title)
    prompt_hash = int(hashlib.sha256(prompt.encode('utf-8')).hexdigest(), 16) % 10 ** 16

    return DataFrame([
        OpenAiQuery(
            id=f"{user_id}_{prompt_hash}",
            user_id=user_id,
            prompt=prompt,
            category="is_exec",
            prompt_hash=prompt_hash,
        )
    ])


# common for all open ai questions
@online
def get_openai_answer(
    prompt: OpenAiQuery.prompt,
) -> OpenAiQuery.prompt_result:
    prompt_hash = int(hashlib.sha256(prompt.encode('utf-8')).hexdigest(), 16) % 10 ** 16
    # result = openai_client.get_completion(prompt.encode('utf-8'))

    return OpenAiQueryResult(
        id=prompt_hash,
        result='yes' # result,
    )


@online
def get_openai_is_director(
    result: User.open_ai_queries[OpenAiQuery.category=="is_exec"].prompt_result,
) -> User.is_exec:
    return result[0].result.lower() in ("yes", "true")


@online
def dummy_users() -> DataFrame[User.id, User.title]:
    return DataFrame(
        [
            User(id=1, title="CEO"),
            User(id=2, title="Queen of Scots"),
            User(id=3, title='VP of Finance'),
            User(id=4, title='SWE'),
        ]
        )
