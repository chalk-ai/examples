from chalk.features import DataFrame, features, has_many


@features
class Book:
    id: str
    name: str
    page_count: int
    author_id: str


@features
class Author:
    id: str
    # The `has_many(...)` function takes a lambda function
    # that specifies the join condition between the classes.
    # We need to use a lambda function, not simply the join condition,
    # to allow for forward references to the `Author` class.
    books: DataFrame[Book] = has_many(lambda: Book.author_id == Author.id)


# You can reference the has-many relationship, and interact with the
# dataframe type
book_pages_df: DataFrame[Book.page_count] = Author.books[Book.page_count]
