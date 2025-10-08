from datetime import date, datetime

import chalk.functions as F
import chalk.prompts as P
from chalk.features import (
    DataFrame,
    FeatureTime,
    Primary,
    Vector,
    _,
    embed,
    feature,
    features,
)
from chalk.streams import Windowed, windowed
from pydantic import BaseModel, Field


@features
class Session:
    id: int

    created_at: FeatureTime
    end_at: datetime
    duration: float

    user_id: "User.id"
    user: "User"


@features(tags=["team:ProductAnalytics"])
class EventType:
    name: str

    product_area_type: "ProductArea.type"
    product_area: "ProductArea"

    event_weight: float


@features
class Event:
    id: int
    created_at: FeatureTime

    name: "EventType.name"
    type: "EventType"

    product_area_type: "ProductArea.type"
    product_area: "ProductArea"

    user_id: "User.id"
    user: "User"

    session_id: "Session.id"
    session: "Session"


class StructuredOutput(BaseModel):
    sentiment: str = Field(
        description=(
            "The customer interaction sentiment into one of the following three categories:"
            "'Positive,' 'Neutral,' or 'Negative,'"
            "based on its tone, language, and context."
        ),
    )


@features
class CustomerInteractionSearch:
    q: Primary[str]
    # from chalk.features import embed
    vector: Vector = embed(
        input=lambda: CustomerInteractionSearch.q,
        provider="vertexai",
        model="text-embedding-005",
    )
    query_type: str = "vector"

    results: "DataFrame[CustomerInteractionDocument]"


@features
class CustomerInteractionDocument:
    # result of a vector database query
    query: CustomerInteractionSearch.q = ""
    id: int
    distance: float | None
    query_type: str = "vector"
    message: str


@features
class CustomerInteraction:
    ############ BASE FEATURES PULLED FROM SQL ############

    id: int
    created_at: FeatureTime

    subject: str
    body: str

    communication_channel: (
        str  # e.g., "email", "linkedin", "support_ticket", "ai_bot", "sales_call"
    )
    communication_direction: str  # "inbound" or "outbound"

    # :tags: team:qa, priority:high
    is_positive_interaction_from_llm: bool = _.sentiment_from_llm == "Positive"

    # user_id: str
    user_id: "User.id"
    user: "User"
    user_full_name: str = _.user.first_name + " " + _.user.last_name

    # product_area_id: str
    product_area_type_from_llm: P.PromptResponse = P.run_prompt("Product Area")
    product_area_type: "ProductArea.type" = feature(
        max_staleness="infinity",
        expression=F.json_value(_.llm.response, "$.product_area"),
    )
    product_area: "ProductArea"

    # llm_gui: P.PromptResponse = P.run_prompt("analyze sentiment")
    llm: P.PromptResponse = P.completion(
        model="gpt-4o-mini-2024-07-18",
        max_tokens=8192,
        temperature=0.1,
        top_p=0.1,
        messages=[
            P.message(
                role="system",
                content="""
                You are a helpful and accurate assistant. Your task is to perform sentiment
                analysis on the provided customer interaction. Consider the tone, language, and context
                of the message in your analysis.
                Classify the customer interaction sentiment into one of the following three categories:
                'Positive,' 'Neutral,' or 'Negative,' based on its tone, language, and context.
                """,
            ),
            P.message(
                role="user",
                content=F.jinja(
                    """
                    Customer Interaction: {{ CustomerInteraction.body }}
                    """,
                ),
            ),
        ],
        output_structure=StructuredOutput,
    )
    sentiment_from_llm: str = feature(
        max_staleness="infinity",
        expression=F.json_value(_.llm.response, "$.sentiment"),
    )


@features
class ProductArea:
    type: str
    description: str | None
    created_at: FeatureTime

    customer_interactions: "DataFrame[CustomerInteraction]"
    total_interactions: Windowed[int] = windowed(
        "7d",
        "30d",
        "90d",
        expression=_.customer_interactions.count(),
    )

    negative_interactions: int = _.customer_interactions[_.sentiment == "Negative"].count()
    positive_interactions: int = _.customer_interactions[_.sentiment == "Positive"].count()
    neutral_interactions: int = _.customer_interactions[_.sentiment == "Neutral"].count()
    nps: float | None = feature(
        max_staleness="30d",
        expression=(100 * (
            (_.positive_interactions / _.customer_interactions.count()) -
            (_.negative_interactions / _.customer_interactions.count()))
        ),
    )


# pip install chalkpy
# from chalk import features
@features(owner="elvisk@chalk.ai")
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    birthday: date
    created_at: FeatureTime

    username: str
    # import chalk.functions as F
    name_match_score: float = F.jaccard_similarity(
        F.lower(_.first_name) + " " + F.lower(_.last_name),
        F.lower(_.username),
    )

    sessions: "DataFrame[Session]"
    average_session_duration: float = _.sessions[_.duration].mean()
    session_count: Windowed[int] = windowed(
        "30d",
        "60d",
        "90d",
        expression=_.sessions[_.created_at > _.chalk_window].count(),
    )

    product_events: "DataFrame[Event]"
    top_10_mobile_events: list[str] = feature(
        max_staleness="7d",
        expression=_.product_events[
            _.type.name,
            _.product_area == "mobile",
        ].approx_top_k(k=10),
    )
