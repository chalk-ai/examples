from datetime import date, datetime
from enum import Enum

from chalk.features import features


class Genre(Enum):
    FICTION = "FICTION"
    NONFICTION = "NONFICTION"
    DRAMA = "DRAMA"
    POETRY = "POETRY"


# The @features decorator creates a feature for each attribute
# of the class. These feature classes work a lot like Python's
# dataclasses, except that you can construct them with only
# partial arguments.
@features
class Book:
    # Features can be any primitive Python type
    id: int
    name: str
    pages: int
    publish_date: date
    copyright_ended_at: datetime | None
    genre: Genre

    # Features can also be lists and sets of any primitive
    authors: list[str]
    categories: set[str]

    # Descriptions live as comments above features.
    # See 05_feature_discovery/4_descriptions.py for more information.
    jacket_copy: str


# Note that we don't supply all the arguments to book here
anna_karenina = Book(name="Anna Karenina", pages=864)

# Feature classes can be easily converted to dictionaries
assert dict(anna_karenina) == {
    "book.name": "Anna Karenina",
    "book.pages": 864,
}
