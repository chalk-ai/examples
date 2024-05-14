from chalk import online
from chalk.features import features, has_many, DataFrame, before_all

from openai import OpenAI

import hashlib
import os
from functools import lru_cache

openai_client: OpenAI


@lru_cache
def hash_prompt(prompt: str, length=16) -> str:
    """Hash a prompt to a fixed length string. This is useful for caching open ai API requests"""
    return int(hashlib.sha256(prompt.encode('utf-8')).hexdigest(), 16) % 10 ** length


@before_all
def initialize_open_ai_client():
    # Note, one should be cautious when using global to give access to custom
    # data sources: https://docs.chalk.ai/docs/generic#scopes
    global openai_client

    openai_client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPEN_AI_API_KEY"),
    )


# A list of prompts that we can run based on our user's titles
title_prompts = dict(
    is_exec="Does the job title `{title}` mean that the person is a executive at their company? Please answer with one word, either: `Yes` or `No`.",
    is_swe="Does the job title `{title}` mean the person is a software engineer? Please answer with one word, either: `Yes` or `No`"
)


@features
class OpenAiQuery:
    id: str
    user_id: str
    # this is one of `is_exec`, `other_quest`, random_question (it is is the question "type")
    category: str
    prompt: str
    prompt_hash: str
    prompt_result: "OpenAiQueryResult"


# By setting a high max scaleness, we can cache the openai query, limiting our api calls
# for users with equivalent titles
@features(max_staleness="1000d")
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
    is_exec_prompt = title_prompts["is_exec"].format(title=title)
    prompt_hash = hash_prompt(is_exec_prompt)

    open_ai_title_queries = []
    for category, title_prompt in title_prompts.items():
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
    return result[0].result.lower() in ("yes", "true")


@online
def get_openai_is_swe(
    result: User.open_ai_queries[OpenAiQuery.category == "is_swe"].prompt_result,
) -> User.is_swe:
    """does openai think our user is a software engineer?"""
    return result[0].result.lower() in ("yes", "true")


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
