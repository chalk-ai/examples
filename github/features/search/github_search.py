# trunk-ignore-all(ruff/N812)
import chalk.functions as F
import chalk.prompts as P
from chalk.features import (
    DataFrame,
    Primary,
    Vector,
    _,
    embed,
    features,
)
from pydantic import BaseModel, Field

from src.github.features import GithubRepoDocVDB
from src.github.features.cerebras.cerebras import (
    CEREBRAS_API_KEY,
    CEREBRAS_BASE_URL,
    CEREBRAS_MODEL,
    CEREBRAS_MODEL_PROVIDER,
)

from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)

CHAT_MAX_TOKENS: int = 8192
CHAT_TEMPERATURE: float = 0.1
CHAT_TOP_P: float = 0.1


class StructuredOutput(BaseModel):
    repo_url: str = Field(
        description="The URL of the best matching GitHub repository",
    )
    confidence: float = Field(
        description="The confidence threshold for the generated summary, between 0 and 1",
    )
    summary: str = Field(
        description="What this repo does and why it was selected",
    )


@features
class GithubSearch:
    query: Primary[str]
    limit: int = 10
    vector: Vector[768] = embed(
        input=lambda: GithubSearch.query,
        provider="vertexai",  # openai
        model="text-embedding-005",  # text-embedding-3-small
    )

    results: DataFrame[GithubRepoDocVDB]
    urls_in_list: list[str] = F.array_agg(
        expr=_.results[_.url],
    )
    urls_in: str = F.array_join(
        arr=_.urls_in_list,
        delimiter="\n\n====\n\n",
    )

    individual_descriptions: list[str] = F.array_agg(
        expr=_.results[_.ai_summary],
    )
    descriptions: str = F.array_join(
        arr=_.individual_descriptions,
        delimiter="\n\n====\n\n",
    )

    distances_in_list: list[float] = F.array_agg(
        expr=_.results[_.distance,],
    )

    # https://chalk.ai/projects/dmo5dhaj3yqu/environments/dvxenv/prompts
    # Can also edit prompts from the dashboard
    # completion_gui: P.PromptResponse = P.run_prompt("repo_summary")
    completion: P.PromptResponse = P.completion(
        api_key=CEREBRAS_API_KEY,
        model_provider=CEREBRAS_MODEL_PROVIDER,
        model=CEREBRAS_MODEL,
        base_url=CEREBRAS_BASE_URL,
        max_tokens=CHAT_MAX_TOKENS,
        temperature=CHAT_TEMPERATURE,
        top_p=CHAT_TOP_P,
        messages=[
            P.message(
                role="system",
                content=SYSTEM_PROMPT,
            ),
            P.message(
                role="user",
                content=F.jinja(USER_PROMPT),
            ),
        ],
        output_structure=StructuredOutput,
    )

    c_url: str = F.json_value(
        _.completion.response,
        "$.repo_url",
    )
    c_confidence: float = F.json_value(
        _.completion.response,
        "$.confidence",
    )
    c_summary: str = F.json_value(
        _.completion.response,
        "$.summary",
    )
