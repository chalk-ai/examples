from datetime import datetime

import chalk.functions as F
import chalk.prompts as P
import httpx
from chalk.features import (
    DataFrame,
    Features,
    Primary,
    _,
    features,
    has_many,
    has_one,
    online,
)
from httpx import ConnectError
from pydantic import BaseModel, Field

from src.github.features import (
    GithubRepo,
    GithubUser,
)
from src.github.features.cerebras.cerebras import (
    CEREBRAS_API_KEY,
    CEREBRAS_BASE_URL,
    CEREBRAS_MODEL,
    CEREBRAS_MODEL_PROVIDER,
)

# from src.github.features.groq.groq import (
#     GROQ_MODEL,
#     GROQ_BASE_URL,
#     GROQ_API_KEY,
#     GROQ_MODEL_PROVIDER,
# )
from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)

CHAT_MAX_TOKENS: int = 8192
CHAT_TEMPERATURE: float = 0.1
CHAT_TOP_P: float = 0.1


@features
class GithubEvent:
    id: int
    type: str
    created_at: datetime
    public: bool
    payload_action: str | None

    username: str
    is_chalk_repo: bool = _.username == "chalk-ai"

    repo_id: GithubRepo.id
    repo_name: str
    repo: GithubRepo

    username: GithubUser.name
    user: GithubUser

    repo_path: str


@online
def get_url_from_event(
    repo_name: GithubEvent.repo_name,
    username: GithubEvent.username,
) -> GithubEvent.repo_path:
    return f"https://github.com/{username}/{repo_name}"


class StructuredOutput(BaseModel):
    fraud_score: float = Field(
        description="value between 0.0 and 1.0",
    )
    explanation: str = Field(
        description="brief summary of the reasoning",
    )


@features
class GithubFraud:
    username: Primary[str]
    user: GithubUser | None = has_one(
        lambda: GithubFraud.username == GithubUser.name,
    )

    repo: GithubRepo
    repo_path: GithubRepo.path = "okcashpro/okcash"

    twitter_url: str
    user_website_status_code: int | None

    f08_p_of_llm_weight: float = 0.2
    f08_score_just_profile_stats: float

    f09_fraud_p_with_random_socials: float
    f09_fraud_p_with_no_socials: float

    f09_score_without_socials: float
    f10_score_with_socials: float
    f11_delta: float = _.f10_score_with_socials - _.f08_score_just_profile_stats

    events: DataFrame[GithubEvent] = has_many(
        lambda: GithubFraud.username == GithubEvent.username,
    )
    events_with_repo: DataFrame[GithubEvent] = has_many(
        lambda: (GithubFraud.username == GithubEvent.username)
        & (GithubFraud.repo_path == GithubEvent.repo_name),
    )

    f18_archive_event_count: int = _.events.count()
    f17_archive_star_count: int = _.events[_.type == "WatchEvent"].count()

    f14_star_date: datetime | None = F.element_at(
        arr=F.array_agg(
            expr=_.events_with_repo[
                _.created_at,
                _.type == "WatchEvent",
            ],
        ),
        index=0,
    )
    f14_star_date_delta_days: float | None = F.if_then_else(
        condition=F.is_null(_.f14_star_date),
        if_true=None,
        if_false=F.round(
            value=(F.total_seconds(_.f14_star_date - _.user.created_at) / 86400),
            digits=None,
        ),
    )
    f14_star_date_delta_days_str: str
    f15_score_with_star_date: float | None

    f18_archive_star_to_event_proportion: float = (
        _.f17_archive_star_count / _.f18_archive_event_count
    )
    f19_p_from_activity_with_github_archive: float
    f20_score_with_github_archive: float
    f21_delta: float

    llm: P.PromptResponse = P.completion(
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
    f21_llm_explanation: str = F.json_value(
        _.llm.response,
        "$.explanation",
    )
    f21_llm_p_social: float = F.json_value(
        _.llm.response,
        "$.fraud_score",
    )
    f22_llm_score_and_profile_stats: float
    f23_original_score_with_social_and_profile_stats: float = _.f10_score_with_socials
    f24_delta: float = (
        _.f22_llm_score_and_profile_stats
        - _.f23_original_score_with_social_and_profile_stats
    )


#     user_repos_json: str
#     repo_forks: int
#     repo_forks_p: float = _.repo_forks / _.user.public_repos
#
#
# @online
# def get_user_repos_json(
#     url: GithubFraud.user.url_repos,
# ) -> GithubFraud.user_repos_json:
#     return httpx.get(
#         url=url,
#     ).text
#
#
# @online
# def get_user_repos_that_are_forks(
#     json_str: GithubFraud.user_repos_json,
# ) -> GithubFraud.repo_forks:
#     if not json_str:
#         return None
#
#     json_dict = orjson.loads(json_str)
#     return sum(1 for item in json_dict if item.get("fork") is True)


@online
def get_fraud_score_with_socials(
    p_profile_stats: GithubFraud.f08_score_just_profile_stats,
    p_socials: GithubFraud.f09_fraud_p_with_random_socials,
) -> GithubFraud.f10_score_with_socials:
    difference_term = p_socials - p_profile_stats
    scalar = 0.64
    if difference_term > 0.0:
        multiplier = 1.0 + (difference_term**scalar)
    else:
        multiplier = (-difference_term) ** ((1 - scalar) * scalar)
    return max(0.0, min(1.0, multiplier * p_profile_stats))


@online
def get_fraud_score_with_star_date_against_repo(
    score_with_socials: GithubFraud.f10_score_with_socials,
    days: GithubFraud.f14_star_date_delta_days,
) -> GithubFraud.f15_score_with_star_date:
    if days is None:
        return None

    exponent = 2
    tapering_scale = max(0.0, 1.0 - (days / 21.0) ** exponent)
    score = score_with_socials * 0.30 + tapering_scale * 0.70
    return min(max(score, score_with_socials), 1.0)


@online
def get_fraud_score_with_activity_from_github_archive(
    score_with_star_date: GithubFraud.f15_score_with_star_date,
    score_with_socials: GithubFraud.f10_score_with_socials,
    p_from_github_archive: GithubFraud.f19_p_from_activity_with_github_archive,
) -> Features[
    GithubFraud.f20_score_with_github_archive,
    GithubFraud.f21_delta,
]:
    if score_with_star_date is None:
        baseline = score_with_socials
    else:
        baseline = score_with_star_date

    score = baseline * 0.37 + p_from_github_archive * 0.63
    return GithubFraud(
        f20_score_with_github_archive=score,
        f21_delta=score - baseline,
    )


@online
def get_fraud_score_just_profile_stats(
    repo_count_raw: GithubFraud.user.public_repos,
    gists: GithubFraud.user.public_gists,
    followers: GithubFraud.user.followers,
    following: GithubFraud.user.following,
) -> GithubFraud.f08_score_just_profile_stats:
    repo_weight = 0.2375
    gists_weight = 0.2075
    followers_weight = 0.1875
    following_weight = 0.2675

    repo_count = float(repo_count_raw)
    repo_probability = (
        0.75 if repo_count < 1 else max(0.05, 1.0 - (min(repo_count, 10.0) / 20.0))
    )
    gists_probability = min(1.0, 1.0 / (float(gists) + 1.0))
    followers_probability = min(1.0, ((2.0 - float(followers)) / 2.0) ** 2.0)
    following_probability = min(1.0, ((15.0 - float(following)) / 15.0) ** 2.0)

    fraud_probability = (
        (repo_weight * repo_probability)
        + (gists_weight * gists_probability)
        + (followers_weight * followers_probability)
        + (following_weight * following_probability)
    ) * 0.77
    return min(max(fraud_probability, 0.0), 1.0)


@online
def get_p_for_socials(
    f06_user_bio: GithubFraud.user.bio,
    f06_user_company: GithubFraud.user.company,
    f06_user_location: GithubFraud.user.location,
    f06_user_twitter_username: GithubFraud.user.twitter_username,
    f06_user_blog_status_code: GithubFraud.user_website_status_code,
    llm_weight: GithubFraud.f08_p_of_llm_weight,
) -> GithubFraud.f09_fraud_p_with_random_socials:
    blog_weight = 0.20
    bio_weight = 0.32
    company_weight = 0.21
    location_weight = 0.12
    twitter_weight = 0.15

    social_score = 0.0
    if f06_user_bio is None or len(f06_user_bio) == 0:
        social_score += bio_weight
    if f06_user_company is None or len(f06_user_company) == 0:
        social_score += company_weight
    if f06_user_location is None or len(f06_user_location) == 0:
        social_score += location_weight
    if f06_user_twitter_username is None or len(f06_user_twitter_username) == 0:
        social_score += twitter_weight
    if f06_user_blog_status_code is None or f06_user_blog_status_code == 0:
        social_score += blog_weight

    fraud_score = social_score * (1.0 - llm_weight)
    if f06_user_blog_status_code == -1:
        social_score += blog_weight

    return min(max(fraud_score, 0.0), 1.0)


@online
def get_star_date_delta_days(
    delta: GithubFraud.f14_star_date_delta_days,
) -> GithubFraud.f14_star_date_delta_days_str:
    if delta is None:
        return "Did not star this repo"

    if delta in {0, 1}:
        return "Starred within a day of acct creation"

    return f"Starred {delta} days after account creation"


@online
def get_fraud_score_for_github_archive(
    events: GithubFraud.f18_archive_event_count,
    proportion: GithubFraud.f18_archive_star_to_event_proportion,
) -> GithubFraud.f19_p_from_activity_with_github_archive:
    max_base_score = 1.0
    penalty_scale = 0.35
    event_penalty_factor = 1.0 / ((1.0 + events) ** 2)
    proportion_penalty_factor = proportion / (1.0 + proportion)
    penalty = penalty_scale * event_penalty_factor * proportion_penalty_factor
    event_factor = min(1.0, events / 50.0)
    event_score = max_base_score * (1.0 - event_factor)
    proportion_factor = proportion**2
    proportion_score = max_base_score * proportion_factor
    adjusted_score = proportion_score - penalty + event_score
    return min(max(adjusted_score, 0.0), max_base_score)


@online
def get_twitter_url(
    twitter: GithubFraud.user.twitter_username,
) -> GithubFraud.twitter_url:
    if twitter is None:
        return ""

    return f"https://x.com/{twitter}"


def get_user_blog_as_link(
    user_blog: GithubFraud.user.blog,
) -> GithubFraud.user_website_status_code:
    if not user_blog:
        return 0

    if user_blog:
        url = "https://" + user_blog
        try:
            response = httpx.get(
                url=url,
            )
            return response.status_code

        except ConnectError:
            return -1
    return None


@online
def get_fraud_score_with_no_socials(
    p_profile_stats: GithubFraud.f08_score_just_profile_stats,
    p_socials: GithubFraud.f09_fraud_p_with_random_socials,
) -> GithubFraud.f09_score_without_socials:
    difference_term = p_socials - p_profile_stats
    scalar = 0.64
    if difference_term > 0.0:
        multiplier = 1.0 + (difference_term**scalar)
    else:
        multiplier = (-difference_term) ** ((1 - scalar) * scalar)
    return max(0.0, min(1.0, multiplier * p_profile_stats))


@online
def get_fraud_score_with_socials_llm(
    p_profile_stats: GithubFraud.f08_score_just_profile_stats,
    p_socials: GithubFraud.f21_llm_p_social,
) -> GithubFraud.f22_llm_score_and_profile_stats:
    difference_term = p_socials - p_profile_stats
    scalar = 0.64
    if difference_term > 0.0:
        multiplier = 1.0 + (difference_term**scalar)
    else:
        multiplier = (-difference_term) ** ((1 - scalar) * scalar)
    return max(0.0, min(1.0, multiplier * p_profile_stats))


@online
def get_p_for_empty_socials(
    llm_weight: GithubFraud.f08_p_of_llm_weight,
) -> GithubFraud.f09_fraud_p_with_no_socials:
    f06_user_bio = None
    f06_user_company = None
    f06_user_location = None
    f06_user_twitter_username = None
    f06_user_blog_status_code = None

    blog_weight = 0.20
    bio_weight = 0.32
    company_weight = 0.21
    location_weight = 0.12
    twitter_weight = 0.15

    social_score = 0.0
    if f06_user_bio is None or len(f06_user_bio) == 0:
        social_score += bio_weight
    if f06_user_company is None or len(f06_user_company) == 0:
        social_score += company_weight
    if f06_user_location is None or len(f06_user_location) == 0:
        social_score += location_weight
    if f06_user_twitter_username is None or len(f06_user_twitter_username) == 0:
        social_score += twitter_weight
    if f06_user_blog_status_code is None or f06_user_blog_status_code == 0:
        social_score += blog_weight

    fraud_score = social_score * (1.0 - llm_weight)
    if f06_user_blog_status_code == -1:
        social_score += blog_weight

    return min(max(fraud_score, 0.0), 1.0)
