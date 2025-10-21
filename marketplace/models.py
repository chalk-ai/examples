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

from src.marketplace.interaction.interaction_type import InteractionType


@features
class Interaction:
    id: int
    created_at: FeatureTime
    interaction_type: InteractionType

    item_id: "Item.id"
    item: "Item"

    user_id: "User.id"
    user: "User"

    seller_id: "Seller.id"
    seller: "Seller"

    review: "Review"

    price: float | None


@features
class Seller:
    id: int
    created_at: datetime
    zipcode: str

    name: str
    email: str
    phone_number: str

    username: str

    interactions: "DataFrame[Interaction]"


class StructuredOutput(BaseModel):
    sentiment: str = Field(
        description=(
            "The review's sentiment into one of the following three categories:"
            "'Positive,' 'Neutral,' or 'Negative,'"
            "based on its tone, language, and context."
        ),
    )


@features
class ReviewSearch:
    q: Primary[str]
    # from chalk.features import embed
    vector: Vector = embed(
        input=lambda: ReviewSearch.q,
        provider="vertexai",
        model="text-embedding-005",
    )
    query_type: str = "vector"

    results: "DataFrame[ReviewDocument]"


@features
class ReviewDocument:
    # result of a vector database query
    query: ReviewSearch.q = ""
    id: int
    distance: float | None
    query_type: str = "vector"
    title: str


@features
class Review:
    ############ BASE FEATURES PULLED FROM SQL ############

    id: "Interaction.id"
    created_at: FeatureTime

    review_headline: str
    review_body: str

    ### From Salesforce
    phone: float | None
    account_name: str | None
    salesforce_lookup_success: str | None
    ###

    # :tags: team:qa, priority:high
    star_rating: int = feature(min=1, max=5)

    ############ BASE FEATURES PULLED FROM SQL ############

    ############ Computed features ############
    is_positive_review_inline: bool = _.star_rating >= 4
    is_positive_review_from_llm: bool = _.sentiment_from_llm == "Positive"

    normalized_rating: float
    is_positive_review_python_resolver: bool
    ############ Computed features ############

    # item_id: str
    item_id: "Item.id"
    item: "Item"

    # user_id: str
    user_id: "User.id"
    user: "User"

    reviewer_name: str = _.user.first_name + " " + _.user.last_name

    # id: Interaction.id
    interaction: "Interaction"

    # seller_id: str
    seller_id: "Seller.id"
    seller: "Seller"

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
                analysis on the provided Amazon review. Consider the tone, language, and context
                of the review in your analysis.
                Classify the review's sentiment into one of the following three categories:
                'Positive,' 'Neutral,' or 'Negative,' based on its tone, language, and context.
                """,
            ),
            P.message(
                role="user",
                content=F.jinja(
                    """
                    Review: {{ Review.review_body }}
                    Item: {{ Review.item.title }}
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
class ItemPrice:
    id: Primary[int]
    # :tags: team:finance
    value: float
    created_at: datetime

    item_id: "Item.id"
    item: "Item"

    seller_id: "Seller.id"
    seller: "Seller"


@features(tags=["team:DevX"])
class Item:
    id: str
    title: str
    genre_from_llm: str = feature(max_staleness="infinity")
    genre_from_llm_confidence: float = feature(max_staleness="infinity")
    genre_from_llm_reasoning: str = feature(max_staleness="infinity")

    reviews: "DataFrame[Review]"
    average_rating: float | None = _.reviews[_.star_rating].mean()
    total_reviews: int = _.reviews.count()

    review_count: Windowed[int] = windowed(
        "30d",
        "60d",
        "90d",
        "180d",
        "360d",
        expression=_.reviews[_.created_at > _.chalk_window].count(),
    )

    prices: "DataFrame[ItemPrice]"
    times_purchased: int = _.prices.count()
    average_price: float | None = _.prices[_.value].mean()
    most_recent_price: float | None = _.prices[_.value].max_by(_.created_at)


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

    reviews: "DataFrame[Review]"
    review_count: int = _.reviews.count()
    average_rating_given: float | None = _.reviews[_.star_rating].mean()

    # import chalk.functions as F
    name_match_score: float = F.jaccard_similarity(
        F.lower(_.first_name) + " " + F.lower(_.last_name),
        F.lower(_.username),
    )

    interactions: "DataFrame[Interaction]"

    average_purchase_price: float | None = _.interactions[_.price, _.interaction_type == "orderPlacement"].mean()

    top_genres: list[str] = feature(
        max_staleness="30d",
        expression=_.interactions[
            _.item.genre_from_llm,
            _.interaction_type == "productInquiry"
        ].approx_top_k(k=10)
    )

@features
class UserItem:
    id: str = _.user_id + "-" + _.item_id

    user_id: "User.id"
    user: "User"

    item_id: "Item.id"
    item: "Item"

    # import chalk.functions as F
    price_diff: float = F.abs(_.item.most_recent_price - _.user.average_purchase_price)
    price_diff_ratio: float = _.price_diff / _.user.average_purchase_price
    affordability_cap: float = F.sigmoid(_.price_diff_ratio)
    price_fit: float = 1 / (1 + _.price_diff_ratio**2)
