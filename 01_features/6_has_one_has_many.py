from chalk.features import features, DataFrame, has_many


@features
class Book:
    id: str
    name: str
    page_count: int
    author_id: str
    # Here, we do not define the has_one relationship.
    # The relationship is assumed to be symmetric, and the join
    # condition is taken from the `has_many(...)` defined on `Author`.
    author: "Author"


@features
class Author:
    id: str
    books: DataFrame[Book] = has_many(lambda: Book.author_id == Author.id)
