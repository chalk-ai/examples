from chalk.queries.named_query import NamedQuery

from . import Review

NamedQuery(
    name="review",
    input=[Review.id],
    output=[
        # Review features
        Review.review_body,
        Review.review_headline,
        Review.star_rating,
        Review.is_positive_review_inline,
        Review.is_positive_review_python_resolver,
        Review.is_positive_review_from_llm,
        Review.normalized_rating,
        Review.sentiment_from_llm,
        Review.reviewer_name,
        Review.created_at,
        # Product features
        Review.item.title,
        Review.item.genre_with_llm_from_title,
        Review.item.average_rating,
        Review.item.total_reviews,
        # User features
        Review.user.first_name,
        Review.user.last_name,
        Review.user.created_at,
        Review.user.username,
        Review.user.name_match_score,
        Review.user.top_genres,
        # Seller features
        Review.seller.name,
        Review.seller.zipcode,
    ],
)

NamedQuery(
    name="review_dag",
    input=[Review.id],
    output=[
        # Base features pulled from SQL
        Review.id,
        Review.created_at,
        Review.review_headline,
        Review.review_body,
        Review.star_rating,
        # Computed features
        Review.is_positive_review_inline,
        Review.is_positive_review_python_resolver,
        Review.is_positive_review_from_llm,
        Review.normalized_rating,
        # Product information
        Review.item_id,
        Review.item.title,
        Review.item.genre_with_llm_from_title,
        Review.item.genre_with_llm_from_title_confidence,
        Review.item.genre_with_llm_from_title_reasoning,
        Review.item.average_rating,
        Review.item.total_reviews,
        Review.item.review_count,
        Review.interaction.id,
        Review.interaction.created_at,
        Review.interaction.interaction_type,
        # User information
        Review.reviewer_name,
        Review.user.id,
        Review.user.first_name,
        Review.user.last_name,
        Review.user.username,
        Review.user.email,
        Review.user.birthday,
        Review.user.review_count,
        Review.user.average_rating_given,
        # Seller information
        Review.seller.id,
        Review.seller.created_at,
        Review.seller.name,
        Review.seller.zipcode,
        Review.seller.email,
        Review.seller.phone_number,
        # Sentiment analysis features
        Review.llm,
        Review.sentiment_from_llm,
    ],
)
