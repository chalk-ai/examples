from chalk import online

from src.marketplace import Review, User


@online
def get_normalized_rating(
    review_rating: Review.star_rating,
    review_count_across_all_books: Review.item.total_reviews,
    average_rating_across_all_books: Review.item.average_rating,
) -> Review.normalized_rating:
    minimum_reviews: float = review_count_across_all_books / 10
    return (
        review_count_across_all_books
        / (review_count_across_all_books + minimum_reviews)
    ) * review_rating + (
        minimum_reviews / (review_count_across_all_books + minimum_reviews)
    ) * average_rating_across_all_books


@online
def is_positive_review_from_python_resolver(
    bayesian_normalized_rating: Review.normalized_rating,
) -> Review.is_positive_review_python_resolver:
    return bayesian_normalized_rating >= 3.5


@online
def get_username(email: User.email) -> User.username:
    # def get_username(email: str) -> str:
    username = email.split("@")[0]
    if "gmail.com" in email:
        username = username.split("+")[0].replace(".", "")

    return username.lower()
