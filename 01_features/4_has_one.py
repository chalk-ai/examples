from chalk.features import features, has_one


@features
class Author:
    id: str
    author_name: str


@features
class Book:
    id: str
    name: str
    author_id: str
    # The `has_one(...)` function takes a lambda function
    # that specifies the join condition between the classes.
    # We need to use a lambda function, not simply the join condition,
    # to allow for forward references to the `Author` class.
    author: Author = has_one(lambda: Book.author_id == Author.id)


# You can reference features through this has-one relationship
author_name_type = Book.author.author_name
