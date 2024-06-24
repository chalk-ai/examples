from chalk import online
from chalk.features import features, has_many, DataFrame, before_all

import hashlib
import os
from functools import lru_cache

from openai import OpenAI

openai_client: OpenAI

# A list of prompts that we can run based on our user's titles
TITLE_PROMPTS = dict(
    is_exec="Does the job title `{title}` mean that the person is a executive at their company? Please answer with one word, either: `Yes` or `No`.",
    is_swe="Does the job title `{title}` mean the person is a software engineer? Please answer with one word, either: `Yes` or `No`"
)


@lru_cache
def hash_prompt(prompt: str, length=16) -> str:
    """Hash a prompt to a fixed length string. This is useful for caching open ai API requests"""
    return int(hashlib.sha256(prompt.encode('utf-8')).hexdigest(), 16) % 10 ** length


def get_openai_yes_no_answer(response: str) -> bool | None:
    """Tests whether the response is a yes or no answer. If it is ambiguous, returns None."""
    yes = 'yes' in response
    no = 'no' in response
    if (yes and no) or len(response) > 50:
        # our answer is a bit ambiguous, let's not make a decision
        return None
    if yes:
        return True
    if no:
        return False


@before_all
def initialize_open_ai_client():
    # Note, one should be cautious when using global to give access to custom
    # data sources: https://docs.chalk.ai/docs/generic#scopes
    global openai_client

    openai_client = OpenAI(
        # This assumes that the OPEN_AI_API_KEY is set in your chalk
        # deployment: https://docs.chalk.ai/docs/env-vars
        api_key=os.environ.get("OPEN_AI_API_KEY"),
    )


@features
class OpenAiQuery:
    id: str
    user_id: str
    # currently, this is one of `is_exec` or `is_swe` (it is is the question "type")
    category: str
    prompt: str
    prompt_hash: str
    prompt_result: "OpenAiQueryResult"


# Setting no max staleness caches our openai queries, limiting our api calls
# for users with equivalent titles.
@features(max_staleness="infinity")
class OpenAiQueryResult:
    id: str
    result: str
    queries: DataFrame[OpenAiQuery] = has_many(lambda: OpenAiQuery.prompt_hash == OpenAiQueryResult.id)


@features
class User:
    id: str
    title: str
    is_exec: bool
    is_swe: bool
    open_ai_queries: DataFrame[OpenAiQuery] = has_many(lambda: User.id == OpenAiQuery.user_id)


@online
def get_openai_title_queries(
    user_id: User.id,
    title: User.title,
) -> User.open_ai_queries:
    open_ai_title_queries = []
    for category, title_prompt in TITLE_PROMPTS.items():
        prompt = title_prompt.format(title=title)
        prompt_hash = hash_prompt(prompt)
        open_ai_title_queries.append(
            OpenAiQuery(
                id=f"{user_id}_{prompt_hash}",
                user_id=user_id,
                prompt=prompt,
                category=category,
                prompt_hash=prompt_hash,
            )
        )
    return DataFrame(open_ai_title_queries)


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


@online
def get_openai_is_director(
    result: User.open_ai_queries[OpenAiQuery.category == "is_exec"].prompt_result,
) -> User.is_exec:
    """does openai think our user is a director?"""
    try:
        result_cleaned = result[0].result.lower()
        return get_openai_yes_no_answer(result_cleaned)
    except IndexError:
        return None


@online
def get_openai_is_swe(
    result: User.open_ai_queries[OpenAiQuery.category == "is_swe"].prompt_result,
) -> User.is_swe:
    """does openai think our user is a software engineer?"""
    try:
        result_cleaned = result[0].result.lower()
        return get_openai_yes_no_answer(result_cleaned)
    except IndexError:
        return None


@online
def dummy_users() -> DataFrame[User.id, User.title]:
    """Creates some dummy users for us to test"""
    return DataFrame(
        [
            User(id=1, title="CEO"),
            User(id=2, title="Queen of Scots"),
            User(id=3, title='VP of Finance'),
            User(id=4, title='SWE'),
            User(id=5, title='Principal Software Engineer'),
            User(id=6, title='Ingénieur Logiciel'),
        ]
    )
